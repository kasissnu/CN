from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer

log = core.getLogger()

class FlowAnalyzer(object):
    def __init__(self):
        core.openflow.addListeners(self)
        # Periodically request stats every 10 seconds (Dynamic Update)
        Timer(10, self._request_stats, recurring=True)

    def _request_stats(self):
        for connection in core.openflow._connections.values():
            connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
        log.info("Sent flow stats requests to all switches.")

    def _handle_FlowStatsReceived(self, event):
        stats = event.stats
        dpid = dpid_to_str(event.connection.dpid)
        print(f"\n--- Flow Table Analysis for Switch: {dpid} ---")
        
        for f in stats:
            # Identification of Active vs Unused Rules
            status = "ACTIVE" if f.packet_count > 0 else "UNUSED"
            print(f"Rule: Match={f.match}, Packets={f.packet_count}, Bytes={f.byte_count}, Status={status}")

def launch():
    core.registerNew(FlowAnalyzer)
    # Ensure a basic forwarding logic is also running so flows exist
    import pox.forwarding.l2_learning
    pox.forwarding.l2_learning.launch()
