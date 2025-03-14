#include "PlatformCreator.h"
#include "SimpleStandardJobScheduler.h"
#include <wrench.h>
#include <cstdlib>


std::tuple<simgrid::s4u::Link*, simgrid::s4u::Host*> PlatformCreator::create_wms(sg4::NetZone* root) {
    // Create the WMSHost host with its disk
    const std::string hostname = _platform_spec["wms"]["hostname"];
    const std::string speed = "10000000Gf";
    auto wms_host = root->add_host(hostname, speed);
    wms_host->set_core_count(1);
    std::string disk_read_bandwidth;
    try {
        disk_read_bandwidth = _platform_spec["wms"]["disk_read_bandwidth"];
    } catch (nlohmann::detail::type_error &e) {
        throw std::invalid_argument("Invalid disk_read_bandwidth value for wms: " + std::string(e.what()));
    }

    std::string disk_write_bandwidth;
    try {
        disk_write_bandwidth = _platform_spec["wms"]["disk_write_bandwidth"];
    } catch (nlohmann::detail::type_error &e) {
        throw std::invalid_argument("Invalid disk_write_bandwidth value for wms: " + std::string(e.what()));
    }

    auto wms_disk = wms_host->add_disk("wms_disk",
                                          disk_read_bandwidth,
                                          disk_write_bandwidth);
    wms_disk->set_property("size", "5000PiB");
    wms_disk->set_property("mount", "/");

    const std::string link_name = "wms_link";
    std::string link_bandwidth;
    try {
        link_bandwidth = _platform_spec["wms"]["network_bandwidth"];
    } catch (nlohmann::detail::type_error &e) {
        throw std::invalid_argument("Invalid link_bandwidth value for wms: " + std::string(e.what()));
    }
    auto wms_link = root->add_link(link_name, link_bandwidth);
    return std::make_tuple(wms_link, wms_host);
}

std::vector<std::tuple<simgrid::s4u::Link*, simgrid::s4u::Host*>> PlatformCreator::create_workers(sg4::NetZone* root) {
    std::vector<std::tuple<simgrid::s4u::Link*, simgrid::s4u::Host*>> workers;

    for (auto& [hostname, worker_spec] : _platform_spec["workers"].items()) {
        try {
            if (!worker_spec["active"].get<bool>())
                continue;
        } catch (nlohmann::detail::type_error &e) {
            throw std::invalid_argument("Invalid active value for worker: " + std::string(e.what()));
        }

        std::string speed = worker_spec["speed"];
        try {
            speed = worker_spec["speed"];
        } catch (nlohmann::detail::type_error &e) {
            throw std::invalid_argument("Invalid speed value for worker: " + std::string(e.what()));
        }

        auto worker_host = root->add_host(hostname, speed);
        try {
            worker_host->set_core_count(worker_spec["num_cores"].get<int>());
        } catch (nlohmann::detail::type_error &e) {
            throw std::invalid_argument("Invalid num_cores value for worker: " + std::string(e.what()));
        }
        std::string link_name = "link_" + hostname;
        std::string link_bandwidth;
        try {
            link_bandwidth = worker_spec["network_bandwidth"];
        } catch (nlohmann::detail::type_error &e) {
            throw std::invalid_argument("Invalid network_bandwidth value for worker: " + std::string(e.what()));
        }
        auto worker_link = root->add_link(link_name, link_bandwidth);
        workers.emplace_back(worker_link, worker_host);

    }
    return workers;
}

void PlatformCreator::create_platform() {
    // Get the top-level zone
    auto zone = simgrid::s4u::Engine::get_instance()->get_netzone_root();

    // Create the wms host
    auto wms = this->create_wms(zone);

    // Create all the worker hosts
    auto workers = this->create_workers(zone);


    // Create all routes
    for (auto const& worker : workers) {
        sg4::LinkInRoute link1{std::get<0>(wms)};
        sg4::LinkInRoute link2{std::get<0>(worker)};
        zone->add_route(std::get<1>(wms),
                        std::get<1>(worker),
                        {link1, link2});
    }

    zone->seal();
}
