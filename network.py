#!/usr/bin/env python3
# encoding: utf-8

from seedemu import *
import os, sys

def run(dumpfile=None):
    ###############################################################################
    # Simple platform detection
    if dumpfile is None:
        script_name = os.path.basename(__file__)

        if len(sys.argv) == 1:
            platform = Platform.AMD64
        elif len(sys.argv) == 2 and sys.argv[1].lower() == 'arm':
            platform = Platform.ARM64
        else:
            platform = Platform.AMD64

    ###############################################################################
    # Initialize emulator layers
    emu     = Emulator()
    base    = Base()
    routing = Routing()
    ebgp    = Ebgp()
    ibgp    = Ibgp()
    ospf    = Ospf()
    web     = WebService()

    ###############################################################################
    # Create ONE Internet Exchange (IX-100)
    ix100 = base.createInternetExchange(100)
    ix100.getPeeringLan().setDisplayName('MiniNet-IX100')

    ###############################################################################
    # Create FOUR Autonomous Systems
    # AS1 and AS2 are transit networks
    # AS10 and AS11 are stub networks (end-user networks)

    Makers.makeTransitAs(base, 1, [100], [])
    Makers.makeTransitAs(base, 2, [100], [])

    Makers.makeStubAsWithHosts(emu, base, 10, 100, hosts_per_as=1)
    Makers.makeStubAsWithHosts(emu, base, 11, 100, hosts_per_as=1)

    ###############################################################################
    # Peering rules (very simple)
    # AS1 and AS2 peer at IX100 using route server
    ebgp.addRsPeers(100, [1, 2])

    # Stub networks buy transit from AS1
    ebgp.addPrivatePeerings(100, [1], [10, 11], PeerRelationship.Provider)

    ###############################################################################
    # Add layers into the emulator
    emu.addLayer(base)
    emu.addLayer(routing)
    emu.addLayer(ebgp)
    emu.addLayer(ibgp)
    emu.addLayer(ospf)
    emu.addLayer(web)

    ###############################################################################
    # Render / Compile
    if dumpfile is not None:
        emu.dump(dumpfile)

