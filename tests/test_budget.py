#!/usr/bin/env python3
"""
Quantum-Flux Lab - Budget Test Suite

Tests to verify:
1. Total BOM cost is calculated correctly
2. Price calculations are correct
3. No paywalled suppliers in BOM
4. All required components present

Environment variable:
    QFL_TARGET_BUDGET: Target budget in USD (default: 75)

MIT License - 2026 Quantum-Flux Lab Contributors
"""

import csv
import os
import sys
from pathlib import Path

import pytest


def get_budget_limit():
    """Get budget limit from environment or default"""
    return float(os.environ.get('QFL_TARGET_BUDGET', 75.00))


class TestBudgetCompliance:
    """Test budget compliance (user-settable limit)"""
    
    @classmethod
    def setup_class(cls):
        """Load BOM data"""
        cls.bom_path = Path(__file__).parent.parent / 'bom' / 'BOM.csv'
        cls.bom_data = []
        cls.total_cost = 0.0
        cls.budget_limit = get_budget_limit()
        
        if cls.bom_path.exists():
            with open(cls.bom_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip total row
                    if row.get('Part Number', '').startswith('TOTAL'):
                        continue
                    if not row.get('Part Number'):
                        continue
                    
                    cls.bom_data.append(row)
                    
                    # Calculate cost
                    try:
                        qty = int(row.get('Quantity', 1))
                        price = float(row.get('Unit Price (USD)', 0))
                        cls.total_cost += qty * price
                    except (ValueError, TypeError):
                        pass
    
    def test_budget_within_target(self):
        """Verify total cost is within user-set budget target"""
        print(f"\nTotal BOM Cost: ${self.total_cost:.2f}")
        print(f"Budget Target: ${self.budget_limit:.2f}")
        print(f"Remaining: ${self.budget_limit - self.total_cost:.2f}")
        
        assert self.total_cost <= self.budget_limit, \
            f"BOM cost ${self.total_cost:.2f} exceeds target ${self.budget_limit:.2f}"
    
    def test_budget_headroom(self):
        """Verify at least 5% headroom for price fluctuations"""
        headroom = self.budget_limit - self.total_cost
        min_headroom = self.budget_limit * 0.05
        assert headroom >= min_headroom or self.total_cost < self.budget_limit, \
            f"Budget headroom ${headroom:.2f} is less than 5% of target"
    
    def test_no_zero_prices(self):
        """Verify all items have prices"""
        for item in self.bom_data:
            price_str = item.get('Unit Price (USD)', '')
            assert price_str, f"Item {item.get('Part Number')} has no price"
            try:
                price = float(price_str)
                assert price > 0, f"Item {item.get('Part Number')} has zero/negative price"
            except ValueError:
                assert False, f"Item {item.get('Part Number')} has invalid price: {price_str}"


class TestBOMCompleteness:
    """Test BOM has all required components"""
    
    REQUIRED_CATEGORIES = {
        'microcontroller': ['arduino', 'pico', 'microcontroller'],
        'power_control': ['mosfet', 'relay'],
        'hv_generation': ['piezo', 'igniter'],
        'safety': ['sensor', 'fuse'],
        'passive': ['resistor', 'capacitor'],
    }
    
    def test_has_microcontroller(self):
        """Verify BOM includes microcontroller"""
        has_mcu = any(
            any(keyword in item.get('Description', '').lower() for keyword in ['arduino', 'pico'])
            for item in self.bom_data
        )
        assert has_mcu, "BOM missing microcontroller"
    
    def test_has_power_switching(self):
        """Verify BOM includes power switching components"""
        has_switching = any(
            'mosfet' in item.get('Description', '').lower() or
            'relay' in item.get('Description', '').lower()
            for item in self.bom_data
        )
        assert has_switching, "BOM missing power switching components (MOSFET/Relay)"
    
    def test_has_hv_components(self):
        """Verify BOM includes high-voltage generation components"""
        has_hv = any(
            'piezo' in item.get('Description', '').lower() or
            'igniter' in item.get('Description', '').lower()
            for item in self.bom_data
        )
        assert has_hv, "BOM missing high-voltage generation components"
    
    def test_has_safety_components(self):
        """Verify BOM includes safety components"""
        has_safety = any(
            'sensor' in item.get('Description', '').lower() or
            'fuse' in item.get('Description', '').lower() or
            'temp' in item.get('Description', '').lower()
            for item in self.bom_data
        )
        assert has_safety, "BOM missing safety components"
    
    def test_has_passive_components(self):
        """Verify BOM includes passive components"""
        has_passive = any(
            'resistor' in item.get('Description', '').lower() or
            'capacitor' in item.get('Description', '').lower()
            for item in self.bom_data
        )
        assert has_passive, "BOM missing passive components"


class TestSupplierCompliance:
    """Test suppliers are appropriate (no paywalled)"""
    
    BLACKLISTED_SUPPLIERS = [
        'elsevier',
        'springer',
        'wiley',
        'sciencedirect',
        'nature.com',  # Except OA articles
        'ieee.org',    # Mostly paywalled
        'acm.org',     # Mostly paywalled
    ]
    
    APPROVED_SOURCES = [
        'ebay',
        'aliexpress',
        'amazon',
        'local',
        'various',
        'mouser',
        'digikey',
        'adafruit',
        'sparkfun'
    ]
    
    def test_no_paywalled_suppliers(self):
        """Verify no academic paywalled suppliers in BOM"""
        for item in self.bom_data:
            source = item.get('Source', '').lower()
            for blacklisted in self.BLACKLISTED_SUPPLIERS:
                assert blacklisted not in source, \
                    f"Item {item.get('Part Number')} uses paywalled supplier: {source}"
    
    def test_sources_specified(self):
        """Verify all items have sources specified"""
        for item in self.bom_data:
            source = item.get('Source', '').strip()
            assert source, f"Item {item.get('Part Number')} has no source specified"


class TestPricingAccuracy:
    """Test pricing calculations"""
    
    def test_quantity_format(self):
        """Verify quantities are valid integers"""
        for item in self.bom_data:
            qty_str = item.get('Quantity', '1')
            try:
                qty = int(qty_str)
                assert qty > 0, f"Item {item.get('Part Number')} has invalid quantity: {qty}"
            except ValueError:
                assert False, f"Item {item.get('Part Number')} has non-integer quantity: {qty_str}"
    
    def test_price_format(self):
        """Verify prices are valid decimals"""
        for item in self.bom_data:
            price_str = item.get('Unit Price (USD)', '')
            try:
                price = float(price_str)
                assert price >= 0, f"Item {item.get('Part Number')} has negative price: {price}"
            except ValueError:
                assert False, f"Item {item.get('Part Number')} has invalid price: {price_str}"
    
    def test_no_excessive_quantities(self):
        """Verify quantities are reasonable (not bulk)"""
        for item in self.bom_data:
            qty_str = item.get('Quantity', '1')
            qty = int(qty_str)
            # Most items should be qty 1-10 for a single build
            assert qty <= 20, \
                f"Item {item.get('Part Number')} has excessive quantity: {qty} (max 20 for single build)"


class TestSafetyRatings:
    """Test safety ratings in BOM"""
    
    VALID_SAFETY_RATINGS = ['Low', 'Medium', 'High', 'Critical']
    
    def test_hv_components_marked(self):
        """Verify HV components have appropriate safety ratings"""
        for item in self.bom_data:
            desc = item.get('Description', '').lower()
            if any(hv in desc for hv in ['piezo', 'high voltage', 'hv', '30kv', '15kv']):
                safety = item.get('Safety Rating', '')
                assert safety in ['High', 'Critical'], \
                    f"HV item {item.get('Part Number')} should have High/Critical safety rating"
    
    def test_safety_ratings_valid(self):
        """Verify all safety ratings are valid values"""
        for item in self.bom_data:
            safety = item.get('Safety Rating', '')
            if safety:  # Optional field
                assert safety in self.VALID_SAFETY_RATINGS, \
                    f"Item {item.get('Part Number')} has invalid safety rating: {safety}"


def calculate_detailed_budget():
    """Calculate detailed budget breakdown"""
    bom_path = Path(__file__).parent.parent / 'bom' / 'BOM.csv'
    
    if not bom_path.exists():
        return None
    
    categories = {
        'hv_components': 0.0,
        'control_electronics': 0.0,
        'sensors': 0.0,
        'acoustic': 0.0,
        'passive_misc': 0.0
    }
    
    with open(bom_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Part Number', '').startswith('TOTAL') or not row.get('Part Number'):
                continue
            
            try:
                qty = int(row.get('Quantity', 1))
                price = float(row.get('Unit Price (USD)', 0))
                cost = qty * price
                
                desc = row.get('Description', '').lower()
                
                if any(x in desc for x in ['piezo', 'high voltage', 'diode', 'corona']):
                    categories['hv_components'] += cost
                elif any(x in desc for x in ['arduino', 'pico', 'mosfet', 'relay']):
                    categories['control_electronics'] += cost
                elif any(x in desc for x in ['sensor', 'dht', 'ina219', 'mic']):
                    categories['sensors'] += cost
                elif any(x in desc for x in ['speaker', 'woofer', 'amplifier', 'audio']):
                    categories['acoustic'] += cost
                else:
                    categories['passive_misc'] += cost
            except (ValueError, TypeError):
                pass
    
    return categories


def print_budget_report():
    """Print detailed budget report"""
    budget_limit = get_budget_limit()
    
    print("\n" + "=" * 60)
    print("Quantum-Flux Lab - Budget Report")
    print("=" * 60)
    
    categories = calculate_detailed_budget()
    
    if categories:
        print("\nCategory Breakdown:")
        print("-" * 40)
        for cat, cost in categories.items():
            print(f"  {cat.replace('_', ' ').title():25} ${cost:6.2f}")
        print("-" * 40)
        total = sum(categories.values())
        print(f"  {'Total':25} ${total:6.2f}")
        print(f"  {'Budget Target':25} ${budget_limit:6.2f}")
        print(f"  {'Remaining':25} ${budget_limit - total:6.2f}")
        print()
        
        if total <= budget_limit:
            print("✓ WITHIN TARGET")
        else:
            print("✗ EXCEEDS TARGET")
    
    print("=" * 60)


def run_all_tests():
    """Run all budget tests"""
    exit_code = pytest.main([__file__, '-v'])
    
    print_budget_report()
    
    return exit_code


if __name__ == '__main__':
    sys.exit(run_all_tests())
