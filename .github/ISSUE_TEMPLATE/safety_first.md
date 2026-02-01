---
name: Safety First - Hardware Changes
about: Submit hardware modifications that affect safety systems
title: '[SAFETY] '
labels: safety, hardware
assignees: ''

---

# ⚠️ SAFETY FIRST DECLARATION

**This issue template is MANDATORY for any hardware changes that affect:**
- High voltage circuits (>1kV)
- Safety relays or fail-safes
- Temperature monitoring
- Ozone/UV detection
- Emergency stop mechanisms

---

## Change Summary
Brief description of the hardware modification.

## Safety Checklist
**MUST be completed before this PR can be merged:**

### Circuit Safety
- [ ] **Fail-safe relay**: Relay is Normally Closed (NC), opens on fault
- [ ] **Watchdog timer**: 100ms timeout implemented and tested
- [ ] **MOSFET protection**: Logic-level MOSFET with flyback diode
- [ ] **Fuse protection**: Appropriate fast-blow fuse installed
- [ ] **Bleeder resistors**: HV capacitors discharge within 5 seconds

### Sensor Verification
- [ ] **Temperature sensors**: Tested at 40°C (warning) and 50°C (critical)
- [ ] **Ozone sensor**: Calibrated to 0.08 ppm shutdown threshold
- [ ] **UV sensor**: Positioned at operator eye level
- [ ] **Current sensor**: INA219 reading verified against multimeter

### Physical Safety
- [ ] **E-Stop button**: Mushroom type, prominent location, tested
- [ ] **Warning LEDs**: Yellow (warning) and Red (critical) functional
- [ ] **Buzzer**: 2kHz and 4kHz tones audible from 3 meters
- [ ] **Enclosure**: All HV components behind insulated barriers
- [ ] **Grounding**: All metal chassis properly earth-grounded

## Testing Evidence

### Test 1: Over-Voltage Response
```
Test Voltage: ___ kV
Relay Response: [ ] Opens within 100ms
E-Stop Response: [ ] Immediate shutdown
MOSFET Response: [ ] Gate driven low
Result: PASS / FAIL
```

### Test 2: Over-Temperature Response
```
Test Temperature: ___ °C
Warning Trigger: [ ] At 40°C
Shutdown Trigger: [ ] At 50°C
Recovery: [ ] Auto-reset after cooldown
Result: PASS / FAIL
```

### Test 3: Ozone Response
```
Test Concentration: ___ ppm
Warning Trigger: [ ] At 0.05 ppm
Shutdown Trigger: [ ] At 0.08 ppm
Ventilation: [ ] Auto-activates with alarm
Result: PASS / FAIL
```

### Test 4: Emergency Stop
```
Test Scenario: Operator presses E-stop
Relay State: [ ] Opens immediately
MOSFET State: [ ] Gate low within 10ms
Indicator State: [ ] Red LED + buzzer ON
Recovery: [ ] Requires manual reset
Result: PASS / FAIL
```

## Documentation
- [ ] Updated `Log_safety.log` with new test results
- [ ] Updated wiring diagrams (`diagrams/wiring.mmd`)
- [ ] Updated BOM if components changed (`bom/BOM.csv`)
- [ ] Added safety notes to `docs/MAIN_REPORT.md`

## Photos/Videos
Attach photos of:
1. Modified circuit with annotations
2. Safety components (relay, fuse, E-stop)
3. Test setup showing measurement equipment
4. Video of fail-safe test (recommended)

## Peer Review
**This hardware change must be reviewed by at least one other person:**

Reviewer: @username
Review Date: YYYY-MM-DD
Review Comments:

## Budget Impact
- [ ] No cost change
- [ ] Cost increase: $___ (new total: $___)
- [ ] Cost decrease: $___ (new total: $___)

**Total must remain ≤ $75**

## Final Declaration

**I declare that:**
1. I have personally tested all fail-safe mechanisms described above
2. I understand that improper implementation could result in injury or death
3. I accept full responsibility for any safety issues caused by this change
4. I will promptly address any safety concerns raised by reviewers

**Signed:** _________________  
**Date:** _________________

---

## Maintainer Checklist
- [ ] All safety tests documented and verifiable
- [ ] Circuit reviewed for proper isolation and grounding
- [ ] Budget still ≤ $75
- [ ] Documentation updated
- [ ] CI safety tests pass

**DO NOT MERGE until all items checked by maintainer**
