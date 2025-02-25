#ifndef SCHEDULING_USING_SIMULATION_SIMULATOR_WORKFLOWCREATOR_H
#define SCHEDULING_USING_SIMULATION_SIMULATOR_WORKFLOWCREATOR_H

#include <string>
#include <wrench-dev.h>

class WorkflowCreator {
public:
    static std::shared_ptr<wrench::Workflow> create_workflow(const nlohmann::json& workflow_spec);

    static std::vector<std::tuple<double, std::shared_ptr<wrench::BareMetalComputeService>, std::shared_ptr<
                                      wrench::WorkflowTask>>> processOngoingTasks(
        const nlohmann::json& workflow_spec,
        const std::shared_ptr<wrench::Workflow>& workflow,
        const std::map<std::string, std::shared_ptr<wrench::BareMetalComputeService>>& compute_services_map);

    static std::set<std::shared_ptr<wrench::WorkflowTask>> processTasksOfInterest(
        const nlohmann::json& workflow_spec,
        const std::shared_ptr<wrench::Workflow>& workflow);
};

#endif //SCHEDULING_USING_SIMULATION_SIMULATOR_WORKFLOWCREATOR_H
