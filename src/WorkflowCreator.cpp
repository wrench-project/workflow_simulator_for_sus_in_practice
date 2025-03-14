#include <algorithm>

#include "WorkflowCreator.h"
#include "PlatformCreator.h"
#include "SimpleStandardJobScheduler.h"
#include <wrench.h>
#include <wrench/util/UnitParser.h>

XBT_LOG_NEW_DEFAULT_CATEGORY(workflow_creator, "Log category for WorkflowCreator");


std::shared_ptr<wrench::Workflow> WorkflowCreator::create_workflow(const nlohmann::json& workflow_spec) {
    // Parse the workflow
    // As a performance optimization, in this whole simulator, instead of calling getMinNumCores() and getMaxNumCores(), we just
    // hardcode 1 and 64. Check out the macros.

    std::shared_ptr<wrench::Workflow> workflow;
    std::string workflow_file;
    std::cerr << workflow_spec << "\n";
    try {
        workflow_file = workflow_spec["file"].get<std::string>();
    } catch (const nlohmann::detail::type_error &e) {
        throw std::invalid_argument("Invalid workflow_file value: " + std::string(e.what()));
    }

    std::string reference_flops;
    try {
        reference_flops = workflow_spec["reference_flops"].get<std::string>();
    } catch (const nlohmann::detail::type_error &e) {
        throw std::invalid_argument("Invalid reference_flops value: " + std::string(e.what()));
    }

    try {
        workflow = wrench::WfCommonsWorkflowParser::createWorkflowFromJSON(
            workflow_file,
            reference_flops,
            true,
            false,
            true,
            1,
            64,
            true,
            true,
            false);
    } catch (const std::exception& e) {
        throw std::runtime_error("Error file importing JSON workflow in file " + std::string(workflow_spec["file"]) +
            std::string(": ") + std::string(e.what()));
    }

    // Disable dynamic updates for speed
    workflow->enableTopBottomLevelDynamicUpdates(false);

    // Remove all tasks that are already done
    for (auto const& task_id : workflow_spec["done_tasks"].get<std::vector<std::string>>()) {
        WRENCH_INFO("Removing task %s as it's done", task_id.c_str());
        workflow->removeTask(workflow->getTaskByID(task_id));
    }

    // Update bottom-levers and (why not?) re-enable dynamic updates
    workflow->updateAllTopBottomLevels();
    workflow->enableTopBottomLevelDynamicUpdates(true);

    return workflow;
}

std::vector<std::tuple<double, std::shared_ptr<wrench::BareMetalComputeService>, std::shared_ptr<wrench::WorkflowTask>>>
WorkflowCreator::processOngoingTasks(
    const nlohmann::json& workflow_spec, const std::shared_ptr<wrench::Workflow>& workflow,
    const std::map<std::string, std::shared_ptr<wrench::BareMetalComputeService>>& compute_services_map) {
    std::vector<std::tuple<double, std::shared_ptr<wrench::BareMetalComputeService>, std::shared_ptr<
                               wrench::WorkflowTask>>> to_return;

    for (auto const& spec : workflow_spec["ongoing_tasks"]) {
        double how_far_back;
        try {
            how_far_back = spec["how_far_back"].get<double>();
        } catch (const nlohmann::detail::type_error &e) {
            throw std::invalid_argument("Invalid how_far_back value: " + std::string(e.what()));
        }

        std::string worker_name;
        try {
            worker_name = spec["worker"];
        } catch (const nlohmann::detail::type_error &e) {
            throw std::invalid_argument("Invalid worker value for an ongoing task: " + std::string(e.what()));
        }
        std::string task_name;
        try {
            task_name = spec["task"];
        } catch (const nlohmann::detail::type_error &e) {
            throw std::invalid_argument("Invalid task_name value for an ongoing task: " + std::string(e.what()));
        }
        std::shared_ptr<wrench::BareMetalComputeService> cs = compute_services_map.at(worker_name);
        std::shared_ptr<wrench::WorkflowTask> task = workflow->getTaskByID(task_name);
        to_return.emplace_back(how_far_back, cs, task);
    }

    sort(to_return.begin(), to_return.end(),
         [](const tuple<double, std::shared_ptr<wrench::BareMetalComputeService>, std::shared_ptr<wrench::WorkflowTask>>
            & a,
            const tuple<double, std::shared_ptr<wrench::BareMetalComputeService>, std::shared_ptr<wrench::WorkflowTask>>
            & b) {
             return get<0>(a) > get<0>(b);
         });

    return to_return;
}

std::set<std::shared_ptr<wrench::WorkflowTask>> WorkflowCreator::processTasksOfInterest(
    const nlohmann::json& workflow_spec,
    const std::shared_ptr<wrench::Workflow>& workflow) {
    std::set<std::shared_ptr<wrench::WorkflowTask>> to_return;
    for (std::string id : workflow_spec["interest_tasks"]) {
        to_return.insert(workflow->getTaskByID(id));
    }
    return to_return;
}
