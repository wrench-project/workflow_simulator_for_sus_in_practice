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

XBT_LOG_NEW_DEFAULT_CATEGORY(simple_scheduler_cluster_selection_schemes, "Log category for service selection schemes");

/***************************************************/
/** Setting/Defining the cluster selection scheme **/
/***************************************************/
void SimpleStandardJobScheduler::initWorkerSelectionSchemes() {

    _worker_selection_schemes["fastest_cores"] = [this] (const std::shared_ptr<wrench::WorkflowTask>& task, const std::set<std::shared_ptr<wrench::BareMetalComputeService>>& services) -> std::shared_ptr<wrench::BareMetalComputeService> {
        std::shared_ptr<wrench::BareMetalComputeService> picked = nullptr;
        for (auto const &s : services) {
            if (picked == nullptr) {
                picked = s;
            } else if (_core_flop_rate_map[s] > _core_flop_rate_map[picked]) {
                picked = s;
            } else if ((std::abs<double>(_core_flop_rate_map[s] - _core_flop_rate_map[picked]) < 0.00001)
                       and (s->getHostname() > picked->getHostname())) {
                picked = s;
            }
        }
        return picked;
    };

    _worker_selection_schemes["slowest_cores"] = [this] (const std::shared_ptr<wrench::WorkflowTask>& task, const std::set<std::shared_ptr<wrench::BareMetalComputeService>>& services) -> std::shared_ptr<wrench::BareMetalComputeService> {
        std::shared_ptr<wrench::BareMetalComputeService> picked = nullptr;
        for (auto const &s : services) {
            if (picked == nullptr) {
                picked = s;
            } else if (_core_flop_rate_map[s] < _core_flop_rate_map[picked]) {
                picked = s;
            } else if ((std::abs<double>(_core_flop_rate_map[s] - _core_flop_rate_map[picked]) < 0.00001)
                       and (s->getHostname() > picked->getHostname())) {
                picked = s;
            }
        }
        return picked;
    };

    _worker_selection_schemes["most_idle_cores"] = [this] (const std::shared_ptr<wrench::WorkflowTask>& task, const std::set<std::shared_ptr<wrench::BareMetalComputeService>>& services) -> std::shared_ptr<wrench::BareMetalComputeService> {
        std::shared_ptr<wrench::BareMetalComputeService> picked = nullptr;
        for (auto const &s : services) {
            if (picked == nullptr) {
                picked = s;
            } else {
                if (_idle_cores_map[s] > _idle_cores_map[picked]) {
                    picked = s;
                } else if ((_idle_cores_map[s] == _idle_cores_map[picked]) and (s->getHostname() > picked->getHostname())) {
                    picked = s;
                }
            }
        }
        return picked;
    };

    _worker_selection_schemes["least_idle_cores"] = [this] (const std::shared_ptr<wrench::WorkflowTask>& task, const std::set<std::shared_ptr<wrench::BareMetalComputeService>>& services) -> std::shared_ptr<wrench::BareMetalComputeService> {
        std::shared_ptr<wrench::BareMetalComputeService> picked = nullptr;
        for (auto const &s : services) {
            if (picked == nullptr) {
                picked = s;
            } else {
                if (_idle_cores_map[s] < _idle_cores_map[picked]) {
                    picked = s;
                } else if ((_idle_cores_map[s] == _idle_cores_map[picked]) and (s->getHostname() > picked->getHostname())) {
                    picked = s;
                }
            }
        }
        return picked;
    };

    _worker_selection_schemes["most_idle_cpu_resources"] = [this] (const std::shared_ptr<wrench::WorkflowTask>& task, const std::set<std::shared_ptr<wrench::BareMetalComputeService>>& services) -> std::shared_ptr<wrench::BareMetalComputeService> {
        std::shared_ptr<wrench::BareMetalComputeService> picked = nullptr;
        for (auto const &s : services) {
            if (picked == nullptr) {
                picked = s;
            } else {
                const double s_metric = static_cast<double>(_idle_cores_map[s]) * _core_flop_rate_map[s];
                const double picked_metric = static_cast<double>(_idle_cores_map[picked]) * _core_flop_rate_map[picked];
                if (s_metric > picked_metric) {
                    picked = s;
                } else if ((s_metric == picked_metric) and (s->getHostname() > picked->getHostname())) {
                    picked = s;
                }
            }
        }
        return picked;
    };

}
