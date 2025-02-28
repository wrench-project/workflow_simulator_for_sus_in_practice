/**
 * Copyright (c) 2020. <ADD YOUR HEADER INFORMATION>.
 * Generated with the wrench-init.in tool.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */
#ifndef MY_SIMPLEWMS_H
#define MY_SIMPLEWMS_H

#include <wrench-dev.h>

class SimpleStandardJobScheduler;

/**
 *  @brief A simple WMS implementation
 */
class SimpleWMS : public wrench::ExecutionController {
public:
    SimpleWMS(const std::string& hostname,
              std::shared_ptr<wrench::SimpleStorageService> storage_service,
              std::set<std::shared_ptr<wrench::BareMetalComputeService>> compute_services,
              SimpleStandardJobScheduler* scheduler,
              std::shared_ptr<wrench::Workflow> workflow,
              const std::vector<std::tuple<double, std::shared_ptr<wrench::BareMetalComputeService>, std::shared_ptr<
                                               wrench::WorkflowTask>>>& ongoing_tasks,
              const std::set<std::shared_ptr<wrench::WorkflowTask>>& tasks_of_interest);

    double getTimeOrigin() const { return _time_origin; }

    std::vector<std::tuple<double, std::shared_ptr<wrench::WorkflowTask>, std::shared_ptr<
                               wrench::BareMetalComputeService>>> _completed_tasks;

    double _time_origin = 0;

private:
    int main() override;
    void processEventStandardJobCompletion(const std::shared_ptr<wrench::StandardJobCompletedEvent>& event) override;
    void processEventStandardJobFailure(const std::shared_ptr<wrench::StandardJobFailedEvent>& event) override;
    void startOngoingTasks() const;

    std::shared_ptr<wrench::SimpleStorageService> _storage_service;
    std::set<std::shared_ptr<wrench::BareMetalComputeService>> _compute_services;
    std::shared_ptr<wrench::Workflow> _workflow;
    std::vector<std::tuple<double, std::shared_ptr<wrench::BareMetalComputeService>, std::shared_ptr<wrench::WorkflowTask>>> _ongoing_tasks;
    std::set<std::shared_ptr<wrench::WorkflowTask>> _tasks_of_interest;
    SimpleStandardJobScheduler* _scheduler;

    std::shared_ptr<wrench::JobManager> _job_manager;

    bool _stop_simulation = false;
};

#endif //MY_SIMPLEWMS_H
