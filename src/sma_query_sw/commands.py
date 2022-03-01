commands = {
    "login": {
        "command": 0xFFFD040C,
        "response": 0xFFFD040D
    },
    "logoff": {
        "command": 0xFFFD010E,
        "response": 0xFFFD010F
    },
    "energy_production": {
        "command": 0x54000200,
        "response": 0x54000201,
        "first": 0x00260100,
        "last": 0x002622FF,
        "registers": [{
            "name": "total",
            "offset": 62,
            "invalid": 0x8000000000000000,
            "bytes": 8
        }, {
            "name": "today",
            "offset": 78,
            "invalid": 0x8000000000000000,
            "bytes": 8
        }]
    },
    "spot_ac_power": {
        "command": 0x51000200,
        "response": 0x00464000,
        "first": 0x00464000,
        "last": 0x004642FF,
        "registers": [
            {
                "name": "spot_ac_power",
                "offset": 62,
                "invalid": 0x80000000
            }
        ]
    },
    "spot_ac_voltage": {
        "command": 0x51000200,
        "response": 0x00464800,
        "first": 0x00464800,
        "last": 0x004655FF,
        "registers": [{
            "name": "spot_ac_voltage",
            "offset": 62,
            "invalid": 0xFFFFFFFF
        }, {
            "name": "spot_ac_current",
            "offset": 146,
            "invalid": 0x80000000
        }]
    },
    "spot_dc_power": {
        "command": 0x53800200,
        "response": 0x00251E00,
        "first": 0x00251E00,
        "last": 0x00251EFF,
        "registers": [{
            "name": "spot_dc_power1",
            "offset": 62,
            "invalid": 0x80000000
        }, {
            "name": "spot_dc_power2",
            "offset": 90,
            "invalid": 0x80000000
        }]
    },
    "spot_dc_voltage": {
        "command": 0x53800200,
        "response": 0x00451F00,
        "first": 0x00451F00,
        "last": 0x004521FF,
        "registers": [{
            "name": "spot_dc_voltage1",
            "offset": 62,
            "invalid": 0x80000000
        }, {
            "name": "spot_dc_voltage2",
            "offset": 90,
            "invalid": 0x80000000
        }, {
            "name": "spot_dc_current1",
            "offset": 118,
            "invalid": 0x80000000
        }, {
            "name": "spot_dc_current2",
            "offset": 146,
            "invalid": 0x80000000
        }]
    },
    "grid_frequency": {
        "command": 0x51000200,
        "response": 0x00465700,
        "first": 0x00465700,
        "last":  0x004657FF,
        "registers": [{
            "name": "grid_frequency",
            "offset": 62,
            "invalid": 0xFFFFFFFF
        }]
    },
    "inverter_status": {
        "command": 0x51800200,
        "response": 0x00214800,
        "first": 0x00214800,
        "last": 0x002148FF,
        "registers": [{
            "name": "inverter_status",
            "offset": 62,
            "invalid": 0x80000000
        }]
    },
    "grid_relay_status": {
        "command": 0x51800200,
        "response": 0x00416400,
        "first": 0x00416400,
        "last": 0x004164FF,
        "registers": [{
            "name": "grid_relay_status",
            "offset": 62,
            "invalid": 0x80000000
        }]
    },
    "inverter_temperature": {
        "command": 0x52000200,
        "response": 0x00237700,
        "first": 0x00237700,
        "last": 0x002377FF,
        "registers": [{
            "name": "inverter_temperature",
            "offset": 62,
            "invalid": 0x80000000
        }]
    }
}
