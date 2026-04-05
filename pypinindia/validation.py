"""
Data validation and integrity checks for pypinindia.

Provides schema validation, duplicate detection, and coordinate range validation
to ensure data quality when loading or updating pincode CSV data.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

# --- Constants ---

# Valid 6-digit Indian pincode ranges by postal circle prefix
VALID_PINCODE_PREFIXES = {
    "11": "Delhi",
    "12": "Haryana",
    "13": "Haryana/Punjab",
    "14": "Punjab",
    "15": "Punjab",
    "16": "Punjab/Himachal Pradesh",
    "17": "Himachal Pradesh",
    "18": "Jammu & Kashmir",
    "19": "Jammu & Kashmir",
    "20": "Uttar Pradesh",
    "21": "Uttar Pradesh",
    "22": "Uttar Pradesh",
    "23": "Uttar Pradesh",
    "24": "Uttar Pradesh",
    "25": "Uttar Pradesh",
    "26": "Uttar Pradesh",
    "28": "Uttar Pradesh",
    "30": "Rajasthan",
    "31": "Rajasthan",
    "32": "Rajasthan",
    "33": "Rajasthan",
    "34": "Rajasthan",
    "36": "Gujarat",
    "37": "Gujarat",
    "38": "Gujarat",
    "39": "Gujarat",
    "40": "Maharashtra",
    "41": "Maharashtra",
    "42": "Maharashtra",
    "43": "Maharashtra",
    "44": "Maharashtra",
    "45": "Madhya Pradesh",
    "46": "Madhya Pradesh",
    "47": "Madhya Pradesh",
    "48": "Madhya Pradesh",
    "49": "Madhya Pradesh/Chhattisgarh",
    "50": "Andhra Pradesh/Telangana",
    "51": "Andhra Pradesh/Telangana",
    "52": "Andhra Pradesh/Telangana",
    "53": "Andhra Pradesh/Telangana",
    "56": "Karnataka",
    "57": "Karnataka",
    "58": "Karnataka",
    "59": "Karnataka",
    "60": "Tamil Nadu",
    "61": "Tamil Nadu",
    "62": "Tamil Nadu",
    "63": "Tamil Nadu",
    "64": "Tamil Nadu",
    "67": "Kerala",
    "68": "Kerala",
    "69": "Kerala",
    "70": "West Bengal",
    "71": "West Bengal",
    "72": "West Bengal",
    "73": "West Bengal",
    "74": "West Bengal",
    "75": "Odisha",
    "76": "Odisha",
    "77": "Odisha",
    "78": "Assam",
    "79": "Assam/Northeast",
    "80": "Bihar",
    "81": "Bihar",
    "82": "Bihar/Jharkhand",
    "83": "Jharkhand",
    "84": "Bihar",
    "85": "Bihar",
    "90": "Army Postal Service",
}

# India bounding box (with a small buffer)
INDIA_LAT_MIN, INDIA_LAT_MAX = 6.0, 38.0
INDIA_LON_MIN, INDIA_LON_MAX = 68.0, 98.0

REQUIRED_COLUMNS = [
    "pincode", "officename", "statename", "districtname",
    "taluk", "officetype", "Deliverystatus",
]

VALID_OFFICE_TYPES = {"H.O", "S.O", "B.O"}
VALID_DELIVERY_STATUSES = {"Delivery", "Non-Delivery"}


# --- Result dataclass ---

@dataclass
class ValidationReport:
    """Holds the results of a full data validation run."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.is_valid = False
        logger.error("Validation error: %s", msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)
        logger.warning("Validation warning: %s", msg)

    def summary(self) -> str:
        lines = [
            f"Validation {'PASSED' if self.is_valid else 'FAILED'}",
            f"  Errors  : {len(self.errors)}",
            f"  Warnings: {len(self.warnings)}",
        ]
        for k, v in self.stats.items():
            lines.append(f"  {k}: {v}")
        if self.errors:
            lines.append("Errors:")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append("Warnings:")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)


# --- Validator ---

class DataValidator:
    """
    Validates pincode DataFrame for schema correctness, data integrity,
    duplicate records, and coordinate range compliance.
    """

    def validate(self, df: pd.DataFrame) -> ValidationReport:
        """
        Run all validation checks on the given DataFrame.

        Args:
            df: The pincode DataFrame to validate.

        Returns:
            ValidationReport with errors, warnings, and stats.
        """
        report = ValidationReport()
        report.stats["total_rows"] = len(df)

        self._check_schema(df, report)
        if not report.is_valid:
            # Schema errors are fatal; skip further checks
            return report

        self._check_pincode_format(df, report)
        self._check_pincode_prefix(df, report)
        self._check_duplicates(df, report)
        self._check_null_critical_fields(df, report)
        self._check_office_types(df, report)
        self._check_delivery_statuses(df, report)

        # Coordinate checks only when lat/lon columns are present
        if "Latitude" in df.columns and "Longitude" in df.columns:
            self._check_coordinates(df, report)

        return report

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_schema(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """Verify all required columns are present."""
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            report.add_error(f"Missing required columns: {missing}")

    def _check_pincode_format(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """Ensure every pincode is exactly 6 digits."""
        pincode_col = df["pincode"].astype(str).str.strip()
        invalid_mask = ~pincode_col.str.match(r"^\d{6}$")
        invalid_count = int(invalid_mask.sum())
        if invalid_count:
            samples = pincode_col[invalid_mask].unique()[:5].tolist()
            report.add_error(
                f"{invalid_count} rows have invalid pincode format (not 6 digits). "
                f"Samples: {samples}"
            )
        report.stats["invalid_pincode_format"] = invalid_count

    def _check_pincode_prefix(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """Warn about pincodes whose 2-digit prefix is not a known postal circle."""
        pincode_col = df["pincode"].astype(str).str.strip()
        prefixes = pincode_col.str[:2]
        unknown_mask = ~prefixes.isin(VALID_PINCODE_PREFIXES.keys())
        unknown_count = int(unknown_mask.sum())
        if unknown_count:
            samples = pincode_col[unknown_mask].unique()[:5].tolist()
            report.add_warning(
                f"{unknown_count} rows have unrecognised pincode prefix. "
                f"Samples: {samples}"
            )
        report.stats["unknown_pincode_prefix"] = unknown_count

    def _check_duplicates(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """
        Detect exact duplicate rows and warn about pincodes mapped to
        multiple states (data inconsistency).
        """
        # Exact duplicate rows
        dup_rows = int(df.duplicated().sum())
        if dup_rows:
            report.add_warning(f"{dup_rows} exact duplicate rows found.")
        report.stats["duplicate_rows"] = dup_rows

        # Same pincode → multiple states (suspicious)
        pincode_states = (
            df.groupby(df["pincode"].astype(str).str.strip())["statename"]
            .nunique()
        )
        multi_state = pincode_states[pincode_states > 1]
        if not multi_state.empty:
            samples = multi_state.index[:5].tolist()
            report.add_warning(
                f"{len(multi_state)} pincodes are mapped to more than one state. "
                f"Samples: {samples}"
            )
        report.stats["pincodes_with_multiple_states"] = len(multi_state)

    def _check_null_critical_fields(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """Flag rows where critical fields are null or empty."""
        critical = ["pincode", "statename", "districtname"]
        for col in critical:
            null_count = int(df[col].isna().sum())
            empty_count = int((df[col].astype(str).str.strip() == "").sum())
            total_bad = null_count + empty_count
            if total_bad:
                report.add_warning(
                    f"Column '{col}' has {total_bad} null/empty values."
                )
            report.stats[f"null_empty_{col}"] = total_bad

    def _check_office_types(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """Warn about unexpected office type values."""
        if "officetype" not in df.columns:
            return
        unexpected = set(df["officetype"].dropna().unique()) - VALID_OFFICE_TYPES
        if unexpected:
            report.add_warning(
                f"Unexpected officetype values found: {sorted(unexpected)}"
            )
        report.stats["unexpected_office_types"] = len(unexpected)

    def _check_delivery_statuses(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """Warn about unexpected delivery status values."""
        if "Deliverystatus" not in df.columns:
            return
        unexpected = set(df["Deliverystatus"].dropna().unique()) - VALID_DELIVERY_STATUSES
        if unexpected:
            report.add_warning(
                f"Unexpected Deliverystatus values found: {sorted(unexpected)}"
            )
        report.stats["unexpected_delivery_statuses"] = len(unexpected)

    def _check_coordinates(self, df: pd.DataFrame, report: ValidationReport) -> None:
        """Validate latitude/longitude values fall within India's bounding box."""
        lat = pd.to_numeric(df["Latitude"], errors="coerce")
        lon = pd.to_numeric(df["Longitude"], errors="coerce")

        non_numeric = int(lat.isna().sum() + lon.isna().sum())
        if non_numeric:
            report.add_warning(
                f"{non_numeric} coordinate values could not be parsed as numbers."
            )

        out_of_range_mask = (
            lat.notna() & lon.notna() & (
                (lat < INDIA_LAT_MIN) | (lat > INDIA_LAT_MAX) |
                (lon < INDIA_LON_MIN) | (lon > INDIA_LON_MAX)
            )
        )
        out_count = int(out_of_range_mask.sum())
        if out_count:
            report.add_warning(
                f"{out_count} rows have coordinates outside India's bounding box "
                f"(lat {INDIA_LAT_MIN}–{INDIA_LAT_MAX}, lon {INDIA_LON_MIN}–{INDIA_LON_MAX})."
            )
        report.stats["coordinates_out_of_range"] = out_count
        report.stats["coordinates_non_numeric"] = non_numeric


def validate_dataframe(df: pd.DataFrame) -> ValidationReport:
    """
    Convenience function to validate a pincode DataFrame.

    Args:
        df: DataFrame to validate.

    Returns:
        ValidationReport instance.
    """
    return DataValidator().validate(df)


def validate_coordinates(
    lat: float, lon: float
) -> Tuple[bool, Optional[str]]:
    """
    Check whether a single lat/lon pair falls within India's bounding box.

    Args:
        lat: Latitude value.
        lon: Longitude value.

    Returns:
        (True, None) if valid, (False, reason_string) otherwise.
    """
    if not (INDIA_LAT_MIN <= lat <= INDIA_LAT_MAX):
        return False, (
            f"Latitude {lat} is outside India's range "
            f"[{INDIA_LAT_MIN}, {INDIA_LAT_MAX}]"
        )
    if not (INDIA_LON_MIN <= lon <= INDIA_LON_MAX):
        return False, (
            f"Longitude {lon} is outside India's range "
            f"[{INDIA_LON_MIN}, {INDIA_LON_MAX}]"
        )
    return True, None
