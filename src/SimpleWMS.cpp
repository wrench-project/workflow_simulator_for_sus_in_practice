/**
* Copyright (c) 2020. <ADD YOUR HEADER INFORMATION>.
* Generated with the wrench-init.in tool.
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*/
#include <iostream>
#include <utility>

#include "SimpleWMS.h"
#include "SimpleStandardJobScheduler.h"

XBT_LOG_NEW_DEFAULT_CATEGORY(simple_wms, "Log category for Simple WMS");

/**
* @brief Create a Simple WMS with a workflow instance, a scheduler implementation, and a list of compute services
*/
SimpleWMS::SimpleWMS(const std::string& hostname,
                     std::shared_ptr<wrench::SimpleStorageService> storage_service,
                     std::set<std::shared_ptr<wrench::BareMetalComputeService>> compute_services,
                     SimpleStandardJobScheduler* scheduler,
                     std::shared_ptr<wrench::Workflow> workflow,
                     const std::vector<std::tuple<
                         double, std::shared_ptr<wrench::BareMetalComputeService>, std::shared_ptr<
                             wrench::WorkflowTask>>>& ongoing_tasks,
                     const std::set<std::shared_ptr<wrench::WorkflowTask>>& tasks_of_interest) :
    wrench::ExecutionController(hostname, "simple"),
    _storage_service(std::move(storage_service)),
    _compute_services(std::move(compute_services)),
    _workflow(std::move(workflow)),
    _ongoing_tasks(ongoing_tasks),
    _tasks_of_interest(tasks_of_interest),
    _scheduler(scheduler) {
}


/**
* @brief main method of the SimpleWMS daemon
*/
int SimpleWMS::main() {
    wrench::TerminalOutput::setThisProcessLoggingColor(wrench::TerminalOutput::COLOR_GREEN);

    WRENCH_INFO("About to execute a workflow with %lu tasks", _workflow->getNumberOfTasks());

    // Create a job manager
    _job_manager = this->createJobManager();

    // Initialize the scheduler
    _scheduler->init(_job_manager, _compute_services, _storage_service);

    WRENCH_INFO("Starting the ongoing tasks...");
    startOngoingTasks();

    _time_origin = wrench::Simulation::getCurrentSimulatedDate();
    WRENCH_INFO("The \"real\" time origin is: %lf", _time_origin);

    /* Main simulation loop */
    while (not _workflow->isDone() and not _stop_simulation) {
        // Get the ready tasks
        const auto ready_tasks = _workflow->getReadyTasks();

        // Run ready tasks with defined scheduler implementation
        _scheduler->scheduleTasks(ready_tasks);

        // Wait for a workflow execution event, and process it
        try {
            this->waitForAndProcessNextEvent();
        }
        catch (wrench::ExecutionException& e) {
            WRENCH_INFO("Error while getting next execution event (%s)... ignoring and trying again",
                        (e.getCause()->toString().c_str()));
        }
    }

    // Pretty wild
//    wrench::Simulation::sleep(0.00001);
    return 0;
}

void SimpleWMS::processEventStandardJobCompletion(const std::shared_ptr<wrench::StandardJobCompletedEvent>& event) {
    const auto task = event->standard_job->getTasks().at(0);
    //    std::cerr << wrench::Simulation::getCurrentSimulatedDate() << ": COMPLETED: " << task->getID() << ": " << task->getNumCoresAllocated() << "\n";
    // std::cerr << "JOB COMPLETED: task " << task->getID() << " (" << task->getExecutionHost() << ", " << task->getNumCoresAllocated() << ")\n";
    auto cs = std::dynamic_pointer_cast<wrench::BareMetalComputeService>(event->compute_service);

    // std::cerr << "UPDATING CORES[" << event->compute_service->getHostname() << "] += " << task->getNumCoresAllocated() << "\n";
    _scheduler->_idle_cores_map[std::dynamic_pointer_cast<wrench::BareMetalComputeService>(event->compute_service)] +=
        task->getNumCoresAllocated();

    _completed_tasks.emplace_back(wrench::Simulation::getCurrentSimulatedDate() - _time_origin, task, cs);

    if (_tasks_of_interest.empty()) {
        return;
    } else {
        if (_tasks_of_interest.find(task) != _tasks_of_interest.end()) {
            _tasks_of_interest.erase(task);
        } else {
            return;
        }
        if (_tasks_of_interest.empty()) {
            _stop_simulation = true;
        }
    }
}

void SimpleWMS::processEventStandardJobFailure(const std::shared_ptr<wrench::StandardJobFailedEvent>& event) {
    throw std::runtime_error("Job Failure shouldn't happen: " + event->toString());
}

void SimpleWMS::startOngoingTasks() const {
    double last_task_submit_date;
    for (size_t task_index = 0; task_index < _ongoing_tasks.size(); ++task_index) {
        auto ongoing_task = _ongoing_tasks.at(task_index);
        const auto how_far_back = std::get<0>(ongoing_task);
        auto cs = std::get<1>(ongoing_task);
        auto task = std::get<2>(ongoing_task);

        // If not the first task and not the last task, then sleep the delta with the previous task
        if (task_index > 0) {
            wrench::Simulation::sleep(std::get<0>(_ongoing_tasks.at(task_index - 1)) - how_far_back);
        }
        // Submit task to the worker
        WRENCH_INFO("Submitting ongoing task %s to worker %s (how far back = %lf)", task->getID().c_str(),
                    cs->getHostname().c_str(), how_far_back);
        _scheduler->submitTaskToWorker(task, cs, 1);

        // If the last task, sleep up to the time origin
        if (task_index == _ongoing_tasks.size() - 1) {
            wrench::Simulation::sleep(how_far_back);
        }
    }
}
