/**
 * Copyright (c) 2020. <ADD YOUR HEADER INFORMATION>.
 * Generated with the wrench-init.in tool.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */
#ifndef MY_SIMPLESCHEDULER_H
#define MY_SIMPLESCHEDULER_H

#include <wrench-dev.h>

#include <utility>

#define TASK_MIN_NUM_CORES(task) 1
#define TASK_MAX_NUM_CORES(task) 64


class SimpleStandardJobScheduler {

public:

    explicit SimpleStandardJobScheduler();

    void scheduleTasks(std::vector<std::shared_ptr<wrench::WorkflowTask> > tasks);

    void init(
            std::shared_ptr<wrench::JobManager> job_manager,
            std::set<std::shared_ptr<wrench::BareMetalComputeService>> compute_services,
            std::shared_ptr<wrench::StorageService> storage_service);

    std::string getDocumentation();

    // Should be private, but whatever, convenient for now
    std::unordered_map<std::shared_ptr<wrench::BareMetalComputeService>, double> _core_flop_rate_map;
    std::unordered_map<std::shared_ptr<wrench::BareMetalComputeService>, unsigned long> _idle_cores_map;
    void computeBottomLevels(const std::shared_ptr<wrench::Workflow>& workflow);
    void computeNumbersOfChildren(const std::shared_ptr<wrench::Workflow>& workflow);

    void setTaskSelectionScheme(const std::string& scheme_name);
    void setWorkerSelectionScheme(const std::string& scheme_name);
    void setNumCoresSelectionScheme(const std::string& scheme_name);

private:
    friend class SimpleWMS;

    static std::vector<std::string> stringSplit(const std::string& str, char sep);

    std::string getTaskPrioritySchemeDocumentation();
    std::string getWorkerSelectionSchemeDocumentation();
    std::string getCoreSelectionSchemeDocumentation();

    void computeTaskBottomLevel(const std::shared_ptr<wrench::WorkflowTask>& task);

    void initTaskPrioritySchemes();
    void initWorkerSelectionSchemes();
    void initCoreSelectionSchemes();

    void prioritizeTasks(std::vector<std::shared_ptr<wrench::WorkflowTask>> &tasks) const;
    bool scheduleTask(const std::shared_ptr<wrench::WorkflowTask>& task,
                      std::shared_ptr<wrench::BareMetalComputeService> *picked_service,
                      std::string &picked_host,
                      unsigned long *picked_num_cores);
    void submitTaskToWorker(const std::shared_ptr<wrench::WorkflowTask>& task, const std::shared_ptr<wrench::BareMetalComputeService> &cs, unsigned long num_cores);


    // std::shared_ptr<wrench::FileLocation> pick_location(const std::shared_ptr<wrench::BareMetalComputeService>& compute_service,
    //                                                     const std::shared_ptr<wrench::DataFile>& file);

    bool taskCanRunOn(const std::shared_ptr<wrench::WorkflowTask>& task, const std::shared_ptr<wrench::BareMetalComputeService>& service);


    std::function<bool(const std::shared_ptr<wrench::WorkflowTask> a, const std::shared_ptr<wrench::WorkflowTask> b)> _task_selection_scheme;
    std::function<std::shared_ptr<wrench::BareMetalComputeService> (const std::shared_ptr<wrench::WorkflowTask> task, const std::set<std::shared_ptr<wrench::BareMetalComputeService>> services)> _worker_selection_scheme;
    std::function<unsigned long(const std::shared_ptr<wrench::WorkflowTask> a, const std::shared_ptr<wrench::BareMetalComputeService> service)> _num_cores_selection_scheme;

    std::map<std::string, std::function<bool(const std::shared_ptr<wrench::WorkflowTask> a, const std::shared_ptr<wrench::WorkflowTask> b)>> _task_selection_schemes;
    std::map<std::string, std::function<std::shared_ptr<wrench::BareMetalComputeService> (const std::shared_ptr<wrench::WorkflowTask> task, const std::set<std::shared_ptr<wrench::BareMetalComputeService>> services)>> _worker_selection_schemes;
    std::map<std::string, std::function<unsigned long(const std::shared_ptr<wrench::WorkflowTask> a, const std::shared_ptr<wrench::BareMetalComputeService> service)>> _num_cores_selection_schemes;

    nlohmann::json _scheduler_spec;

    std::shared_ptr<wrench::StorageService> _storage_service;
    std::set<std::shared_ptr<wrench::BareMetalComputeService>> _compute_services;
    std::shared_ptr<wrench::JobManager> _job_manager;

    std::map<std::shared_ptr<wrench::WorkflowTask>, double> _bottom_levels;
    std::map<std::shared_ptr<wrench::WorkflowTask>, unsigned long> _number_children;

};

#endif //MY_SIMPLESCHEDULER_H

