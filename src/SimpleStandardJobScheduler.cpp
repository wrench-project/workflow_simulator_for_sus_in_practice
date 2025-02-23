/**
 * Copyright (c) 2020. <ADD YOUR HEADER INFORMATION>.
 * Generated with the wrench-init.in tool.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */
#include "SimpleStandardJobScheduler.h"

#include <utility>
#include <algorithm>

XBT_LOG_NEW_DEFAULT_CATEGORY(simple_scheduler, "Log category for Simple Scheduler");

SimpleStandardJobScheduler::SimpleStandardJobScheduler() {
    this->initTaskPrioritySchemes();
    this->initWorkerSelectionSchemes();
    this->initCoreSelectionSchemes();
}

void SimpleStandardJobScheduler::init(
    std::shared_ptr<wrench::JobManager> job_manager,
    std::set<std::shared_ptr<wrench::BareMetalComputeService>> compute_services,
    std::shared_ptr<wrench::StorageService> storage_service) {
    _job_manager = std::move(job_manager);
    _storage_service = std::move(storage_service);
    _compute_services = std::move(compute_services);

    // Create idle core map
    for (auto const& cs : _compute_services)
    {
        _idle_cores_map[cs] = cs->getPerHostNumCores().begin()->second;
    }
    // Create core flop rate map
    for (auto const& cs : _compute_services)
    {
        _core_flop_rate_map[cs] = cs->getCoreFlopRate().begin()->second;
    }
}

bool SimpleStandardJobScheduler::taskCanRunOn(const std::shared_ptr<wrench::WorkflowTask>& task,
                                              const std::shared_ptr<wrench::BareMetalComputeService>& service) {
    return _idle_cores_map[service] >= TASK_MIN_NUM_CORES(task);
}

void SimpleStandardJobScheduler::prioritizeTasks(std::vector<std::shared_ptr<wrench::WorkflowTask>>& tasks) const {
    std::sort(tasks.begin(), tasks.end(), _task_selection_scheme);
}

/** Returns true if found something **/
bool SimpleStandardJobScheduler::scheduleTask(const std::shared_ptr<wrench::WorkflowTask>& task,
                                              std::shared_ptr<wrench::BareMetalComputeService>* picked_worker,
                                              std::string& picked_host,
                                              unsigned long* picked_num_cores) {
    // Weed out impossible workers
    std::set<std::shared_ptr<wrench::BareMetalComputeService>> possible_workers;
    for (auto const& s : _compute_services)
    {
        if (this->taskCanRunOn(task, s))
        {
            possible_workers.insert(s);
        }
    }

    if (possible_workers.empty())
    {
        *picked_worker = nullptr;
        *picked_num_cores = 0;
        return false;
    }

    //    std::cerr << "I HAVE SELECTED " << possible_services.size() << " SERVICES THAT COULD WORK\n";
    //    for (auto const &h : possible_services) {
    //        std::cerr << "  - " << h->getName() << "\n";
    //    }

    *picked_worker = _worker_selection_scheme(task, possible_workers);

    //    WRENCH_INFO("PICKING NUM_CORES");

    // *picked_num_cores = this->core_selection_schemes[std::get<2>(
    //     this->enabled_scheduling_algorithms[this->current_scheduling_algorithm])](task, *picked_service);
    // for (auto const& entry : this->idle_cores_map[*picked_service])
    // {
    //     if (entry.second >= *picked_num_cores)
    //     {
    //         picked_host = entry.first;
    //         break;
    //     }
    // }
    *picked_num_cores = 1;

    return true;
}

void SimpleStandardJobScheduler::scheduleTasks(std::vector<std::shared_ptr<wrench::WorkflowTask>> tasks) {
    prioritizeTasks(tasks);
    //    std::cerr << "AFTER PRIORITIZATION: \n";
    //    for (auto const &rt: tasks) {
    //        std::cerr << "READY TASK: " << rt->getID() << ": NC = " << rt->getNumberOfChildren() <<"\n";
    //    }

    // int num_scheduled_tasks = 0;
    //    WRENCH_INFO("SCHEDULING TASKS");
    for (const auto& task : tasks)
    {
        //        WRENCH_INFO("Trying to schedule ready task %s", task->getID().c_str());
        std::shared_ptr<wrench::BareMetalComputeService> picked_service;
        std::string picked_host;
        unsigned long picked_num_cores;

        // WRENCH_INFO("Trying to schedule task %s", task->getID().c_str());
        if (not scheduleTask(task, &picked_service, picked_host, &picked_num_cores))
        {
            // WRENCH_INFO("Wasn't able to schedule task %s", task->getID().c_str());
            continue;
        }

        WRENCH_INFO("Submitting task %s for execution on service at worker %s with %lu cores",
                    task->getID().c_str(),
                    picked_service->getHostname().c_str(),
                    picked_num_cores);

              // num_scheduled_tasks++;

        // Submitting the task as a simple job
        this->submitTaskToWorker(task, picked_service, picked_num_cores);
    }
    //    std::cerr << "DEBUG SCHEDULED " << num_scheduled_tasks << "\n";
    WRENCH_INFO("Done with scheduling tasks as standard jobs");
}


std::string SimpleStandardJobScheduler::getDocumentation() {
    std::string scheduler_doc;
    scheduler_doc = "Scheduling options:\n";
    scheduler_doc += "\t* Task selection schemes:\n";
    scheduler_doc += this->getTaskPrioritySchemeDocumentation();
    scheduler_doc += "\t* Worker selection schemes:\n";
    scheduler_doc += this->getWorkerSelectionSchemeDocumentation();
    scheduler_doc += "\t* Core selection schemes:\n";
    scheduler_doc += this->getCoreSelectionSchemeDocumentation();
    return scheduler_doc;
}


std::string SimpleStandardJobScheduler::getTaskPrioritySchemeDocumentation() {
    std::string documentation;

    for (auto const& e : _task_selection_schemes)
    {
        documentation += "\t\t- " + e.first + "\n";
    }
    return documentation;
}


std::string SimpleStandardJobScheduler::getWorkerSelectionSchemeDocumentation() {
    std::string documentation;

    for (auto const& e : _worker_selection_schemes)
    {
        documentation += "\t\t- " + e.first + "\n";
    }
    return documentation;
}

std::string SimpleStandardJobScheduler::getCoreSelectionSchemeDocumentation() {
    std::string documentation;

    for (auto const& e : _num_cores_selection_schemes)
    {
        documentation += "\t\t- " + e.first + "\n";
    }
    return documentation;
}

std::vector<std::string> SimpleStandardJobScheduler::stringSplit(const std::string& str, char sep) {
    stringstream ss(str);
    std::vector<std::string> tokens;
    string item;
    while (getline(ss, item, sep))
    {
        tokens.push_back(item);
    }
    return tokens;
}

void SimpleStandardJobScheduler::computeNumbersOfChildren(const std::shared_ptr<wrench::Workflow>& workflow) {
    for (auto const& t : workflow->getTasks())
    {
        _number_children[t] = t->getNumberOfChildren();
    }
}


void SimpleStandardJobScheduler::computeBottomLevels(const std::shared_ptr<wrench::Workflow>& workflow) {
    for (auto const& t : workflow->getEntryTasks())
    {
        computeTaskBottomLevel(t);
    }
}

void SimpleStandardJobScheduler::computeTaskBottomLevel(const std::shared_ptr<wrench::WorkflowTask>& task) {
    if (_bottom_levels.find(task) != _bottom_levels.end())
    {
        return;
    }

    double my_bl = task->getFlops();
    double max = 0.0;
    for (const auto& child : task->getChildren())
    {
        computeTaskBottomLevel(child);
        double bl = _bottom_levels[child];
        max = (bl < max ? max : bl);
    }
    _bottom_levels[task] = my_bl + max;
    //    std::cerr << task->getID() << ": " << this->bottom_levels[task] << "\n";
}

void SimpleStandardJobScheduler::submitTaskToWorker(const std::shared_ptr<wrench::WorkflowTask>& task,
                                                    const std::shared_ptr<wrench::BareMetalComputeService>& cs,
                                                    unsigned long num_cores) {
    // Submitting the task as a simple job
    std::map<std::shared_ptr<wrench::DataFile>, std::shared_ptr<wrench::FileLocation>> file_locations;

    // Input files are read from the "best" location
    for (const auto& f : task->getInputFiles())
    {
        file_locations.insert(std::make_pair(f, wrench::FileLocation::LOCATION(_storage_service, f)));
    }

    for (const auto& f : task->getOutputFiles())
    {
        file_locations.insert(std::make_pair(f, wrench::FileLocation::LOCATION(_storage_service, f)));
    }

    // IMPORTANT: Update the idle cores map
    _idle_cores_map[cs] -= num_cores;

    auto job = _job_manager->createStandardJob(task, file_locations);
    //        std::cerr << wrench::Simulation::getCurrentSimulatedDate() << ": SUBMITTING TASK: " << task->getID() << "\n";
    _job_manager->submitJob(job, cs, {
                                {task->getID(), cs->getHostname() + ":" + std::to_string(num_cores)}
                            });
}

void SimpleStandardJobScheduler::setTaskSelectionScheme(const std::string& scheme_name) {
    if (_task_selection_schemes.find(scheme_name) == _task_selection_schemes.end())
    {
        throw std::invalid_argument("Unknown task selection scheme: " + scheme_name);
    }
    _task_selection_scheme = _task_selection_schemes.at(scheme_name);
}

void SimpleStandardJobScheduler::setWorkerSelectionScheme(const std::string& scheme_name) {
    if (_worker_selection_schemes.find(scheme_name) == _worker_selection_schemes.end())
    {
        throw std::invalid_argument("Unknown worker selection scheme: " + scheme_name);
    }
    _worker_selection_scheme = _worker_selection_schemes.at(scheme_name);
}

void SimpleStandardJobScheduler::setNumCoresSelectionScheme(const std::string& scheme_name) {
    if (_num_cores_selection_schemes.find(scheme_name) == _num_cores_selection_schemes.end())
    {
        throw std::invalid_argument("Unknown num_cores selection scheme: " + scheme_name);
    }
    _num_cores_selection_scheme = _num_cores_selection_schemes.at(scheme_name);
}
