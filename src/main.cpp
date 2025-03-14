/**
 * Copyright (c) 2020. <ADD YOUR HEADER INFORMATION>.
 * Generated with the wrench-init.in tool.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */
#include <wrench.h>
#include "SimpleStandardJobScheduler.h"
#include "SimpleWMS.h"
#include "PlatformCreator.h"
#include "WorkflowCreator.h"
#include <memory>
#include <boost/program_options.hpp>
#include <nlohmann/json.hpp>
#include <sys/time.h>

namespace po = boost::program_options;

std::shared_ptr<wrench::Simulation> simulation;

XBT_LOG_NEW_DEFAULT_CATEGORY(workflow_simulator, "Log category for main");

void startServices(nlohmann::json platform_spec,
                   std::set<std::shared_ptr<wrench::BareMetalComputeService>>& compute_services,
                   std::shared_ptr<wrench::SimpleStorageService>& storage_service) {
    for (auto& [hostname, worker_spec] : platform_spec["workers"].items()) {
        //std::string hostname = worker_spec["hostname"];

        if (not worker_spec["active"].get<bool>())
            continue;

        auto cs = simulation->add(
            new wrench::BareMetalComputeService(
                hostname, {hostname},
                "",
                {},
                {}));
        cs->setNetworkTimeoutValue(DBL_MAX);
        compute_services.insert(cs);
    }

    const std::string wms_hostname = platform_spec["wms"]["hostname"];
    storage_service = simulation->add(
        wrench::SimpleStorageService::createSimpleStorageService(
            wms_hostname, {"/"}, {}, {}));
    storage_service->setNetworkTimeoutValue(DBL_MAX);
}

int main(int argc, char** argv) {

    // Declaration of the top-level WRENCH simulation object
    simulation = wrench::Simulation::createSimulation();

    // Initialization of the simulation
    simulation->init(&argc, argv);

    std::string json_input_string;
    nlohmann::json json_input;

    auto scheduler = new SimpleStandardJobScheduler();

    // Define command-line argument options
    po::options_description desc("Allowed arguments");
    desc.add_options()
    ("help",
     "Show this help message\n")
    ("json_input", po::value<std::string>(&json_input_string)->required()->value_name("<Input JSON string>"),
     "JSON input string\n");

    // Parse command-line arguments
    po::variables_map vm;
    po::store(
        po::parse_command_line(argc, argv, desc),
        vm
    );

    try {
        // Print help message and exit if needed
        if (vm.count("help")) {
            std::cerr << desc;
            std::cerr << scheduler->getDocumentation();
            exit(0);
        }
        // Throw whatever exception in case argument values are erroneous
        po::notify(vm);

        try {
            json_input = nlohmann::json::parse(json_input_string);
        } catch (const std::exception& e) {
            cerr << "Error parsing the input JSON: " << e.what() << std::endl;
        }
    }
    catch (std::exception& e) {
        cerr << "Error: " << e.what() << "\n";
        exit(1);
    }

    // Creation of the platform
    try {
        PlatformCreator platform_creator(json_input["platform"]);
        simulation->instantiatePlatform(platform_creator);
    }
    catch (std::exception& e) {
        std::cerr << e.what() << "\n";
        exit(1);
    }

    // Start the services
    std::set<std::shared_ptr<wrench::BareMetalComputeService>> compute_services;
    std::shared_ptr<wrench::SimpleStorageService> storage_service;
    startServices(json_input["platform"], compute_services, storage_service);


    // Create a convenient map of hostname to compute service
    std::map<std::string, std::shared_ptr<wrench::BareMetalComputeService>> compute_services_map;
    for (auto const& service : compute_services) {
        compute_services_map[service->getHostname()] = service;
    }

    // Create the workflow
    auto workflow = WorkflowCreator::create_workflow(json_input["workflow"]);

    // Stage all input files on the Storage Service
    for (const auto& f : workflow->getInputFiles()) {
        storage_service->createFile(f);
    }

    // Create a sorted (by "how far back in the past") vector of tuples of (how far back, Task) for
    // the ongoing tasks
    auto ongoing_tasks = WorkflowCreator::processOngoingTasks(json_input["workflow"], workflow, compute_services_map);

    auto tasks_of_interest = WorkflowCreator::processTasksOfInterest(json_input["workflow"], workflow);

    // Configure the scheduler
    scheduler->setTaskSelectionScheme(json_input["scheduling"]["task_selection_scheme"]);
    scheduler->setWorkerSelectionScheme(json_input["scheduling"]["worker_selection_scheme"]);
    scheduler->setNumCoresSelectionScheme(json_input["scheduling"]["num_cores_selection_scheme"]);
    double scheduling_overhead;
    try {
        scheduling_overhead = json_input["scheduling"]["task_scheduling_overhead"];
    } catch (const nlohmann::detail::type_error& e) {
        std::cerr << "Invalid task_scheduling_overhead value: " << e.what() << std::endl;
        exit(1);
    }
    scheduler->setTaskSchedulingOverhead(scheduling_overhead);;

    // Compute metrics useful for some scheduling algorithms
    scheduler->computeBottomLevels(workflow);
    scheduler->computeNumbersOfChildren(workflow);

    // Create the WMS
    auto wms = simulation->add(
        new SimpleWMS(
            json_input["platform"]["wms"]["hostname"],
            storage_service,
            compute_services,
            scheduler,
            workflow,
            ongoing_tasks,
            tasks_of_interest));

    // Launch the simulation
    timeval begin_sim{}, end_sim{};

    gettimeofday(&begin_sim, nullptr);
    try {
        simulation->launch();
    }
    catch (std::runtime_error& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }
    gettimeofday(&end_sim, nullptr);

    // Output
    nlohmann::json output_json;
    output_json["simulation_time"] = ((static_cast<double>(end_sim.tv_sec) * 1000000 + end_sim.tv_usec) -
        (static_cast<double>(begin_sim.tv_sec) * 1000000 +
            begin_sim.tv_usec)) / 1000000.0;
    output_json["finish_date"] = wrench::Simulation::getCurrentSimulatedDate() - wms->_time_origin;
    nlohmann::json task_completion_dict = nlohmann::json::object();
    for (auto const &task_completion : wms->_completed_tasks) {
        nlohmann::json task_dict = nlohmann::json::object();
        task_dict["start_date"] = std::get<0>(task_completion);
        task_dict["end_date"] = std::get<1>(task_completion);
        task_dict["worker"] = std::get<3>(task_completion)->hostname;
        task_completion_dict[std::get<2>(task_completion)->getID()] = task_dict;
    }
    output_json["task_completions"] = task_completion_dict;
    std::cout << output_json.dump() << std::endl;

    exit(0);
}
