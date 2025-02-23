#include <string>
#include <utility>
#include <vector>
#include <nlohmann/json.hpp>
#include <simgrid/s4u/NetZone.hpp>

namespace sg4 = simgrid::s4u;

class PlatformCreator {
public:
    explicit PlatformCreator(nlohmann::json platform_spec) : _platform_spec(std::move(platform_spec)) {
    }

    void operator()() {
        create_platform();
    }

private:
    nlohmann::json _platform_spec;

    void create_platform();
    std::tuple<simgrid::s4u::Link*, simgrid::s4u::Host*> create_wms(sg4::NetZone* root);
    std::vector<std::tuple<simgrid::s4u::Link*, simgrid::s4u::Host*>> create_workers(sg4::NetZone* root);
};
