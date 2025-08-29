"""
Parameter validation system for policy parameters.
Ensures parameter values are within reasonable bounds and policy constraints.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import warnings
from pydantic import BaseModel, Field, validator

from .parameters import (
    Parameters, TaxBracketParams, WFFParams, IETCParams,
    JSSParams, SPSParams, SLPParams, AccommodationSupplementParams
)


@dataclass
class ValidationResult:
    """Result of parameter validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggested_fixes: List[str]


class ParameterBounds(BaseModel):
    """Define reasonable bounds for policy parameters."""
    
    # Tax bracket bounds
    tax_rate_min: float = Field(0.0, description="Minimum tax rate")
    tax_rate_max: float = Field(0.7, description="Maximum tax rate (70%)")
    tax_threshold_min: float = Field(0.0, description="Minimum tax threshold")
    tax_threshold_max: float = Field(1_000_000.0, description="Maximum tax threshold")
    
    # WFF bounds
    wff_credit_min: float = Field(0.0, description="Minimum WFF credit amount")
    wff_credit_max: float = Field(50_000.0, description="Maximum annual WFF credit")
    wff_abate_rate_min: float = Field(0.0, description="Minimum abatement rate")
    wff_abate_rate_max: float = Field(1.0, description="Maximum abatement rate (100%)")
    wff_threshold_min: float = Field(0.0, description="Minimum WFF threshold")
    wff_threshold_max: float = Field(200_000.0, description="Maximum WFF threshold")
    
    # IETC bounds
    ietc_entitlement_min: float = Field(0.0, description="Minimum IETC entitlement")
    ietc_entitlement_max: float = Field(5_000.0, description="Maximum IETC entitlement")
    ietc_threshold_min: float = Field(0.0, description="Minimum IETC threshold")
    ietc_threshold_max: float = Field(100_000.0, description="Maximum IETC threshold")
    
    # Benefit bounds
    benefit_rate_min: float = Field(0.0, description="Minimum benefit rate")
    benefit_rate_max: float = Field(2_000.0, description="Maximum weekly benefit rate")
    benefit_abate_rate_min: float = Field(0.0, description="Minimum benefit abatement rate")
    benefit_abate_rate_max: float = Field(1.0, description="Maximum benefit abatement rate")


class PolicyParameterValidator:
    """
    Validates policy parameters for consistency and reasonableness.
    """
    
    def __init__(self, bounds: Optional[ParameterBounds] = None):
        self.bounds = bounds or ParameterBounds()
    
    def validate_parameters(self, params: Parameters) -> ValidationResult:
        """
        Comprehensive validation of all parameter components.
        """
        errors = []
        warnings = []
        suggested_fixes = []
        
        # Validate tax brackets
        if params.tax_brackets:
            tax_result = self._validate_tax_brackets(params.tax_brackets)
            errors.extend(tax_result.errors)
            warnings.extend(tax_result.warnings)
            suggested_fixes.extend(tax_result.suggested_fixes)
        
        # Validate WFF parameters
        if params.wff:
            wff_result = self._validate_wff_parameters(params.wff)
            errors.extend(wff_result.errors)
            warnings.extend(wff_result.warnings)
            suggested_fixes.extend(wff_result.suggested_fixes)
        
        # Validate IETC parameters
        if params.ietc:
            ietc_result = self._validate_ietc_parameters(params.ietc)
            errors.extend(ietc_result.errors)
            warnings.extend(ietc_result.warnings)
            suggested_fixes.extend(ietc_result.suggested_fixes)
        
        # Validate benefit parameters
        for benefit_type, benefit_params in [
            ("JSS", params.jss),
            ("SPS", params.sps),
            ("SLP", params.slp)
        ]:
            if benefit_params:
                benefit_result = self._validate_benefit_parameters(benefit_params, benefit_type)
                errors.extend(benefit_result.errors)
                warnings.extend(benefit_result.warnings)
                suggested_fixes.extend(benefit_result.suggested_fixes)
        
        # Cross-parameter validation
        cross_result = self._validate_cross_parameter_consistency(params)
        errors.extend(cross_result.errors)
        warnings.extend(cross_result.warnings)
        suggested_fixes.extend(cross_result.suggested_fixes)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggested_fixes=suggested_fixes
        )
    
    def _validate_tax_brackets(self, tax_params: TaxBracketParams) -> ValidationResult:
        """Validate tax bracket parameters."""
        errors = []
        warnings = []
        suggested_fixes = []
        
        # Check rate bounds
        for i, rate in enumerate(tax_params.rates):
            if rate < self.bounds.tax_rate_min:
                errors.append(f"Tax rate {i+1} ({rate}) below minimum ({self.bounds.tax_rate_min})")
                suggested_fixes.append(f"Set tax rate {i+1} to at least {self.bounds.tax_rate_min}")
            elif rate > self.bounds.tax_rate_max:
                errors.append(f"Tax rate {i+1} ({rate}) above maximum ({self.bounds.tax_rate_max})")
                suggested_fixes.append(f"Set tax rate {i+1} to at most {self.bounds.tax_rate_max}")
        
        # Check threshold bounds
        for i, threshold in enumerate(tax_params.thresholds):
            if threshold < self.bounds.tax_threshold_min:
                errors.append(f"Tax threshold {i+1} ({threshold}) below minimum ({self.bounds.tax_threshold_min})")
            elif threshold > self.bounds.tax_threshold_max:
                warnings.append(f"Tax threshold {i+1} ({threshold}) is very high")
        
        # Check progressive structure
        if len(tax_params.rates) != len(tax_params.thresholds) + 1:
            errors.append("Tax rates and thresholds length mismatch")
            suggested_fixes.append("Ensure tax rates = tax thresholds + 1")
        
        # Check rates are increasing (progressive tax)
        for i in range(1, len(tax_params.rates)):
            if tax_params.rates[i] < tax_params.rates[i-1]:
                warnings.append(f"Tax rate {i+1} ({tax_params.rates[i]}) lower than previous rate - not progressive")
                suggested_fixes.append("Consider increasing tax rates progressively")
        
        # Check thresholds are increasing
        for i in range(1, len(tax_params.thresholds)):
            if tax_params.thresholds[i] <= tax_params.thresholds[i-1]:
                errors.append(f"Tax threshold {i+1} not greater than previous threshold")
                suggested_fixes.append("Ensure tax thresholds increase monotonically")
        
        return ValidationResult(len(errors) == 0, errors, warnings, suggested_fixes)
    
    def _validate_wff_parameters(self, wff_params: WFFParams) -> ValidationResult:
        """Validate Working for Families parameters."""
        errors = []
        warnings = []
        suggested_fixes = []
        
        # Validate credit amounts
        credit_amounts = [
            ("FTC1", wff_params.ftc1),
            ("FTC2", wff_params.ftc2),
            ("IWTC1", wff_params.iwtc1),
            ("IWTC2", wff_params.iwtc2),
            ("BSTC", wff_params.bstc),
            ("MFTC", wff_params.mftc)
        ]
        
        for name, amount in credit_amounts:
            if amount < self.bounds.wff_credit_min:
                errors.append(f"WFF {name} credit ({amount}) below minimum")
            elif amount > self.bounds.wff_credit_max:
                warnings.append(f"WFF {name} credit ({amount}) is very high")
        
        # Validate abatement rates
        abatement_rates = [
            ("First threshold", wff_params.abaterate1),
            ("Second threshold", wff_params.abaterate2),
            ("BSTC abatement", wff_params.bstcabate)
        ]
        
        for name, rate in abatement_rates:
            if rate < self.bounds.wff_abate_rate_min or rate > self.bounds.wff_abate_rate_max:
                errors.append(f"WFF {name} abatement rate ({rate}) out of bounds [0, 1]")
        
        # Validate thresholds
        if wff_params.abatethresh1 >= wff_params.abatethresh2:
            errors.append("WFF first abatement threshold must be less than second threshold")
            suggested_fixes.append("Ensure abatethresh1 < abatethresh2")
        
        # Policy logic checks
        if wff_params.ftc1 <= wff_params.ftc2:
            warnings.append("FTC for first child not higher than subsequent children")
        
        if wff_params.iwtc1 <= wff_params.iwtc2:
            warnings.append("IWTC for first child not higher than subsequent children")
        
        return ValidationResult(len(errors) == 0, errors, warnings, suggested_fixes)
    
    def _validate_ietc_parameters(self, ietc_params: IETCParams) -> ValidationResult:
        """Validate Independent Earner Tax Credit parameters."""
        errors = []
        warnings = []
        suggested_fixes = []
        
        # Validate entitlement
        if not (self.bounds.ietc_entitlement_min <= ietc_params.ent <= self.bounds.ietc_entitlement_max):
            errors.append(f"IETC entitlement ({ietc_params.ent}) out of reasonable bounds")
        
        # Validate threshold
        if not (self.bounds.ietc_threshold_min <= ietc_params.thresh <= self.bounds.ietc_threshold_max):
            errors.append(f"IETC threshold ({ietc_params.thresh}) out of reasonable bounds")
        
        # Validate abatement rate
        if not (0 <= ietc_params.abate <= 1):
            errors.append(f"IETC abatement rate ({ietc_params.abate}) must be between 0 and 1")
        
        # Policy logic
        if ietc_params.thresh < 10000:
            warnings.append("IETC threshold seems low - may affect many low-income earners")
        
        return ValidationResult(len(errors) == 0, errors, warnings, suggested_fixes)
    
    def _validate_benefit_parameters(self, benefit_params: Union[JSSParams, SPSParams, SLPParams], 
                                   benefit_type: str) -> ValidationResult:
        """Validate benefit parameters."""
        errors = []
        warnings = []
        suggested_fixes = []
        
        # Basic rate validation
        if hasattr(benefit_params, 'base_rate'):
            if not (self.bounds.benefit_rate_min <= benefit_params.base_rate <= self.bounds.benefit_rate_max):
                errors.append(f"{benefit_type} base rate ({benefit_params.base_rate}) out of bounds")
        
        # Abatement rate validation
        if hasattr(benefit_params, 'abatement_rate'):
            if not (0 <= benefit_params.abatement_rate <= 1):
                errors.append(f"{benefit_type} abatement rate must be between 0 and 1")
        
        # Income threshold validation
        if hasattr(benefit_params, 'income_threshold'):
            if benefit_params.income_threshold < 0:
                errors.append(f"{benefit_type} income threshold cannot be negative")
        
        return ValidationResult(len(errors) == 0, errors, warnings, suggested_fixes)
    
    def _validate_cross_parameter_consistency(self, params: Parameters) -> ValidationResult:
        """Validate consistency across different parameter types."""
        errors = []
        warnings = []
        suggested_fixes = []
        
        # Check tax vs WFF interaction
        if params.tax_brackets and params.wff:
            # WFF abatement thresholds should align with tax system
            top_tax_threshold = max(params.tax_brackets.thresholds) if params.tax_brackets.thresholds else 0
            
            if params.wff.abatethresh2 > top_tax_threshold * 2:
                warnings.append("WFF second threshold very high compared to top tax bracket")
        
        # Check IETC vs other credits
        if params.ietc and params.wff:
            # IETC threshold should be reasonable relative to WFF
            if params.ietc.thresh > params.wff.abatethresh1:
                warnings.append("IETC threshold higher than WFF first threshold - check targeting")
        
        # Check benefit rates relative to each other
        benefit_rates = []
        if params.jss and hasattr(params.jss, 'base_rate'):
            benefit_rates.append(("JSS", params.jss.base_rate))
        if params.sps and hasattr(params.sps, 'base_rate'):
            benefit_rates.append(("SPS", params.sps.base_rate))
        if params.slp and hasattr(params.slp, 'base_rate'):
            benefit_rates.append(("SLP", params.slp.base_rate))
        
        if len(benefit_rates) > 1:
            rates_only = [rate for _, rate in benefit_rates]
            if max(rates_only) / min(rates_only) > 3:
                warnings.append("Large variation in benefit rates - check policy intention")
        
        return ValidationResult(len(errors) == 0, errors, warnings, suggested_fixes)
    
    def suggest_parameter_improvements(self, params: Parameters) -> List[str]:
        """Suggest improvements to make parameters more policy-coherent."""
        suggestions = []
        
        # Tax system suggestions
        if params.tax_brackets:
            # Check for reasonable progression
            rates = params.tax_brackets.rates
            if len(rates) > 1:
                rate_increases = [rates[i] - rates[i-1] for i in range(1, len(rates))]
                if any(increase > 0.15 for increase in rate_increases):
                    suggestions.append("Consider smaller increments between tax rates to reduce cliff effects")
        
        # WFF suggestions
        if params.wff:
            # Check abatement smoothness
            if abs(params.wff.abaterate1 - params.wff.abaterate2) > 0.1:
                suggestions.append("Consider similar WFF abatement rates to avoid complexity")
        
        return suggestions


def validate_parameter_override(base_params: Parameters, 
                              overrides: Dict[str, Any]) -> ValidationResult:
    """
    Validate parameter overrides before applying them.
    
    Args:
        base_params: Original parameters
        overrides: Dictionary of parameter overrides in dot notation
        
    Returns:
        ValidationResult indicating if overrides are valid
    """
    errors = []
    warnings = []
    suggested_fixes = []
    
    validator = PolicyParameterValidator()
    
    # Create a copy of parameters with overrides applied
    try:
        from .optimisation import _set_nested_attr
        
        modified_params = base_params.model_copy(deep=True)
        
        for path, value in overrides.items():
            try:
                # Validate individual override
                if "tax_brackets.rates" in path and isinstance(value, (int, float)):
                    if not (0 <= value <= 0.7):
                        errors.append(f"Tax rate override {path}={value} out of reasonable bounds [0, 0.7]")
                
                elif "wff." in path and "abate" in path and isinstance(value, (int, float)):
                    if not (0 <= value <= 1):
                        errors.append(f"Abatement rate override {path}={value} must be between 0 and 1")
                
                elif any(keyword in path for keyword in ["threshold", "thresh"]):
                    if isinstance(value, (int, float)) and value < 0:
                        errors.append(f"Threshold override {path}={value} cannot be negative")
                
                # Apply the override
                _set_nested_attr(modified_params, path, value)
                
            except (AttributeError, KeyError, IndexError, TypeError) as e:
                errors.append(f"Invalid parameter path or value: {path}={value} ({str(e)})")
        
        # Validate the modified parameter set
        if not errors:  # Only validate if basic checks passed
            validation_result = validator.validate_parameters(modified_params)
            errors.extend(validation_result.errors)
            warnings.extend(validation_result.warnings)
            suggested_fixes.extend(validation_result.suggested_fixes)
    
    except Exception as e:
        errors.append(f"Failed to apply parameter overrides: {str(e)}")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggested_fixes=suggested_fixes
    )