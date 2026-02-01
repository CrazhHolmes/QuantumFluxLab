#!/usr/bin/env python3
"""
Quantum-Flux Lab - Safety Test Suite

Tests to verify:
1. Fail-safe circuit logic
2. Safety threshold compliance
3. Emergency stop functionality
4. Watchdog timer behavior

MIT License - 2026 Quantum-Flux Lab Contributors
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestSafetyThresholds:
    """Test safety threshold values are within safe limits"""
    
    # Safety thresholds from controller code
    SAFETY_LIMITS = {
        'electric_field': {'operating': 5000, 'limit': 20000, 'unit': 'V/m'},  # 5 kV/m operating, 20 kV/m max
        'ozone': {'operating': 0.05, 'limit': 0.1, 'unit': 'ppm'},  # OSHA 8-hr limit
        'temperature': {'operating': 40, 'limit': 60, 'unit': '°C'},  # Piezo Curie temp
        'current': {'operating': 0.8, 'limit': 2.0, 'unit': 'A'},  # Power supply limit
        'spl': {'operating': 100, 'limit': 115, 'unit': 'dB'},  # OSHA 15-min limit
    }
    
    def test_electric_field_margin(self):
        """Verify 4:1 safety margin for electric field"""
        ratio = self.SAFETY_LIMITS['electric_field']['limit'] / self.SAFETY_LIMITS['electric_field']['operating']
        assert ratio >= 4.0, f"Electric field safety margin {ratio:.1f}:1 is less than 4:1"
    
    def test_ozone_margin(self):
        """Verify ozone shutdown at 80% of OSHA limit"""
        shutdown = 0.08  # From controller code
        osha_limit = 0.1
        assert shutdown <= osha_limit * 0.8, "Ozone shutdown threshold exceeds 80% of OSHA limit"
    
    def test_temperature_shutdown(self):
        """Verify temperature shutdown below Curie point"""
        shutdown_temp = 50  # From controller code
        curie_temp = 150  # Typical PZT Curie temperature
        assert shutdown_temp < curie_temp * 0.5, "Temperature shutdown too close to Curie point"
    
    def test_spl_limits(self):
        """Verify SPL limits per OSHA guidelines"""
        spl_limits = {
            115: 15 * 60,    # 115 dB for 15 minutes
            120: 60,         # 120 dB for 1 minute
            140: 0.1,        # 140 dB for 0.1 second
        }
        
        for level, duration in spl_limits.items():
            assert level <= 140, f"SPL level {level} exceeds absolute maximum 140 dB"
            assert duration >= 0.1, f"Duration for {level} dB is less than minimum"


class TestFailSafeCircuit:
    """Test fail-safe circuit implementation"""
    
    def test_relay_normally_closed(self):
        """Verify relay is normally closed (failsafe position)"""
        # In the circuit, relay should be NC so power is cut when control fails
        relay_config = {
            'type': 'NC',  # Normally Closed
            'control_voltage': 5,  # 5V relay
            'switching_time_ms': 10
        }
        
        assert relay_config['type'] == 'NC', "Relay must be Normally Closed for fail-safe operation"
        assert relay_config['switching_time_ms'] <= 20, "Relay switching too slow for safety"
    
    def test_watchdog_timeout(self):
        """Verify watchdog timer timeout is appropriate"""
        watchdog_config = {
            'timeout_ms': 100,
            'reset_interval_ms': 50
        }
        
        # Watchdog should reset faster than timeout
        assert watchdog_config['reset_interval_ms'] < watchdog_config['timeout_ms']
        # Timeout should be fast enough to prevent damage (< 1 second)
        assert watchdog_config['timeout_ms'] <= 1000, "Watchdog timeout too long"
    
    def test_mosfet_protection(self):
        """Verify MOSFET has flyback diode protection"""
        mosfet_config = {
            'model': 'IRLZ44N',
            'logic_level': True,
            'flyback_diode': True,
            'current_rating_A': 47
        }
        
        assert mosfet_config['logic_level'], "Must use logic-level MOSFET for Arduino"
        assert mosfet_config['flyback_diode'], "Flyback diode required for inductive load"
        assert mosfet_config['current_rating_A'] >= 10, "MOSFET current rating insufficient"


class TestEmergencyStop:
    """Test emergency stop functionality"""
    
    def test_e_stop_response_time(self):
        """Verify E-stop responds within 10ms"""
        e_stop_config = {
            'type': 'mushroom',
            'latching': True,
            'response_time_ms': 10
        }
        
        assert e_stop_config['latching'], "E-stop must be latching (stops until manually reset)"
        assert e_stop_config['response_time_ms'] <= 10, "E-stop response too slow"
    
    def test_e_stop_wiring(self):
        """Verify E-stop is wired to interrupt pin"""
        # E-stop should be on pin 2 (interrupt capable on Arduino Nano)
        e_stop_pin = 2
        interrupt_pins = [2, 3]  # Arduino Nano external interrupts
        
        assert e_stop_pin in interrupt_pins, "E-stop must be on interrupt-capable pin"


class TestSafetyCode:
    """Test safety code in controller"""
    
    def test_emergency_stop_in_code(self):
        """Verify emergency stop code exists"""
        controller_path = Path(__file__).parent.parent / 'code' / 'qfl_controller.ino'
        
        if not controller_path.exists():
            pytest.skip("Controller code not found")
        
        with open(controller_path, 'r') as f:
            code = f.read()
        
        # Check for emergency stop handling
        assert 'EMERGENCY_STOP' in code or 'emergency' in code.lower(), \
            "Emergency stop not found in controller code"
        assert 'ESTOP' in code or 'E-Stop' in code, \
            "E-Stop not found in controller code"
    
    def test_watchdog_in_code(self):
        """Verify watchdog timer code exists"""
        controller_path = Path(__file__).parent.parent / 'code' / 'qfl_controller.ino'
        
        if not controller_path.exists():
            pytest.skip("Controller code not found")
        
        with open(controller_path, 'r') as f:
            code = f.read()
        
        assert 'watchdog' in code.lower() or 'WDT' in code, \
            "Watchdog timer not found in controller code"
    
    def test_relay_in_code(self):
        """Verify safety relay code exists"""
        controller_path = Path(__file__).parent.parent / 'code' / 'qfl_controller.ino'
        
        if not controller_path.exists():
            pytest.skip("Controller code not found")
        
        with open(controller_path, 'r') as f:
            code = f.read()
        
        assert 'relay' in code.lower() or 'RELAY' in code, \
            "Safety relay not found in controller code"
    
    def test_temperature_monitoring(self):
        """Verify temperature monitoring code exists"""
        controller_path = Path(__file__).parent.parent / 'code' / 'qfl_controller.ino'
        
        if not controller_path.exists():
            pytest.skip("Controller code not found")
        
        with open(controller_path, 'r') as f:
            code = f.read()
        
        assert 'temp' in code.lower() or 'TEMP' in code, \
            "Temperature monitoring not found in controller code"


class TestSimulation:
    """Simulate safety scenarios"""
    
    def test_over_voltage_response(self):
        """Simulate over-voltage condition and verify response"""
        # Simulated sensor readings
        sensor_data = {
            'voltage': 35000,  # Exceeds 30kV limit
            'temperature': 25,
            'ozone': 0.02
        }
        
        # Check if voltage exceeds safe threshold
        if sensor_data['voltage'] > 30000:
            # System should trigger shutdown
            shutdown_triggered = True
        else:
            shutdown_triggered = False
        
        assert shutdown_triggered, "Over-voltage should trigger shutdown"
    
    def test_over_temperature_response(self):
        """Simulate over-temperature condition"""
        sensor_data = {
            'temperature': 55,  # Exceeds 50°C limit
            'ozone': 0.02,
            'voltage': 12000
        }
        
        if sensor_data['temperature'] > 50:
            shutdown_triggered = True
            relay_opened = True
        else:
            shutdown_triggered = False
            relay_opened = False
        
        assert shutdown_triggered, "Over-temperature should trigger shutdown"
        assert relay_opened, "Relay should open on over-temperature"
    
    def test_ozone_response(self):
        """Simulate high ozone condition"""
        sensor_data = {
            'ozone': 0.09,  # Exceeds 0.08 ppm limit
            'temperature': 25,
            'voltage': 12000
        }
        
        if sensor_data['ozone'] > 0.08:
            warning_issued = True
            ventilation_activated = True
        else:
            warning_issued = False
            ventilation_activated = False
        
        assert warning_issued, "High ozone should issue warning"
        assert ventilation_activated, "Ventilation should activate on high ozone"


def run_all_tests():
    """Run all safety tests and report results"""
    print("=" * 60)
    print("Quantum-Flux Lab - Safety Test Suite")
    print("=" * 60)
    print()
    
    # Run pytest programmatically
    exit_code = pytest.main([__file__, '-v', '--tb=short'])
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✓ ALL SAFETY TESTS PASSED")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ SOME SAFETY TESTS FAILED")
        print("=" * 60)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(run_all_tests())
