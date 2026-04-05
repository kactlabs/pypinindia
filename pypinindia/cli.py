"""
Command-line interface for pypinindia.
"""

import argparse
import sys
import json
from typing import List, Dict, Any, Optional, Union

from .core import (
    PincodeData, get_pincode_info, get_state, get_district, get_taluk,
    get_offices, search_by_state, search_by_district, get_states, get_districts
)
from .geospatial import get_nearby_pincodes, get_nearest_pincodes, get_pincode_coordinates
from .exceptions import InvalidPincodeError, DataNotFoundError, DataLoadError


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Indian Pincode lookup and information tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pypinindia 110001                    # Get info for pincode 110001
  pypinindia --state 110001            # Get state for pincode
  pypinindia --district 110001         # Get district for pincode
  pypinindia --offices 110001          # Get offices for pincode
  pypinindia --search-state "Delhi"    # Get all pincodes in Delhi
  pypinindia --search-district "Mumbai" --in-state "Maharashtra"
  pypinindia --list-states             # List all states
  pypinindia --list-districts          # List all districts
  pypinindia --stats                   # Show dataset statistics
  pypinindia --nearby 110001 --radius 10 # Find pincodes within 10km of 110001
  pypinindia --nearest --lat 28.6139 --lon 77.2090 --limit 5  # Find 5 nearest pincodes
        """
    )
    
    parser.add_argument(
        "pincode",
        nargs="?",
        help="Pincode to lookup (6-digit number)"
    )
    
    # Geospatial subcommands
    parser.add_argument(
        "--nearby",
        metavar="PINCODE",
        help="Find pincodes near the specified pincode"
    )
    
    parser.add_argument(
        "--nearest",
        action="store_true",
        help="Find nearest pincodes to coordinates (requires --lat and --lon)"
    )
    
    parser.add_argument(
        "--district", "-d",
        action="store_true",
        help="Get district name for the pincode"
    )
    
    parser.add_argument(
        "--taluk", "-t",
        action="store_true",
        help="Get taluk name for the pincode"
    )
    
    parser.add_argument(
        "--offices", "-o",
        action="store_true",
        help="Get office names for the pincode"
    )
    
    parser.add_argument(
        "--search-state",
        help="Search pincodes by state name"
    )
    
    parser.add_argument(
        "--search-district",
        help="Search pincodes by district name"
    )
    
    parser.add_argument(
        "--in-state",
        help="Filter district search by state name"
    )
    
    parser.add_argument(
        "--list-states",
        action="store_true",
        help="List all states in the dataset"
    )
    
    parser.add_argument(
        "--list-districts",
        help="List all districts, optionally filtered by state"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show dataset statistics"
    )
    
    parser.add_argument(
        "--state", "-s",
        action="store_true",
        help="Get state name for the pincode"
    )
    
    parser.add_argument(
        "--radius",
        type=float,
        default=5.0,
        help="Search radius in kilometers for nearby search (default: 5)"
    )
    
    parser.add_argument(
        "--lat", "--latitude",
        type=float,
        help="Latitude for nearest search (decimal degrees)"
    )
    
    parser.add_argument(
        "--lon", "--longitude",
        type=float,
        help="Longitude for nearest search (decimal degrees)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results to return (default: 10)"
    )
    
    parser.add_argument(
        "--coordinates",
        action="store_true",
        help="Get coordinates for the pincode"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    
    parser.add_argument(
        "--data-file",
        help="Path to custom CSV data file"
    )
    
    args = parser.parse_args()
    
    try:
        if args.data_file and args.verbose:
            print(f"Using custom data file: {args.data_file}")

        # Handle geospatial commands
        if args.nearby:
            if not args.nearby.isdigit() or len(args.nearby) != 6:
                print(f"Error: Invalid pincode format '{args.nearby}'. Must be a 6-digit number.", file=sys.stderr)
                sys.exit(1)
            handle_nearby_command(args.nearby, args.radius, args.limit, args.json, args.verbose, args.data_file)
            return
        
        if args.nearest:
            if args.lat is None or args.lon is None:
                parser.error("Both --lat and --lon are required for --nearest command")
            handle_nearest_command(args.lat, args.lon, args.limit, args.json, args.verbose)
            return

        # Handle list operations
        if args.list_states:
            list_states(args.json, args.verbose)
            return

        if args.list_districts:
            list_districts(args.list_districts, args.json, args.verbose)
            return

        if args.stats:
            show_statistics(args.json, args.verbose, args.data_file)
            return

        # Handle search operations
        if args.search_state:
            search_state(args.search_state, args.json, args.verbose, args.data_file)
            return

        if args.search_district:
            search_district(args.search_district, args.in_state, args.json, args.verbose, args.data_file)
            return

        # Handle pincode operations
        if not args.pincode:
            parser.error("Pincode is required unless using search, list, or geospatial options")

        if not args.pincode.isdigit() or len(args.pincode) != 6:
            print(f"Error: Invalid pincode format '{args.pincode}'. Must be a 6-digit number.", file=sys.stderr)
            sys.exit(1)

        lookup_pincode(args.pincode, args, args.data_file)

    except (InvalidPincodeError, DataNotFoundError, DataLoadError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    except InvalidPincodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except DataNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except DataLoadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def lookup_pincode(pincode: str, args: argparse.Namespace, data_file: Optional[str] = None) -> None:
    """Lookup information for a specific pincode."""
    try:
        if args.coordinates:
            coords_result = get_pincode_coordinates(pincode)
            output_result(coords_result, args.json, args.verbose, f"Coordinates for {pincode}")
        
        elif args.state:
            state_result = get_state(pincode) if not data_file else PincodeData(data_file).get_state(pincode)
            output_result(state_result, args.json, args.verbose, f"State for {pincode}")
        
        elif args.district:
            district_result = get_district(pincode) if not data_file else PincodeData(data_file).get_district(pincode)
            output_result(district_result, args.json, args.verbose, f"District for {pincode}")
        
        elif args.taluk:
            taluk_result = get_taluk(pincode) if not data_file else PincodeData(data_file).get_taluk(pincode)
            output_result(taluk_result, args.json, args.verbose, f"Taluk for {pincode}")
        
        elif args.offices:
            offices_result = get_offices(pincode) if not data_file else PincodeData(data_file).get_offices(pincode)
            output_result(offices_result, args.json, args.verbose, f"Offices for {pincode}")
        
        else:
            # Default: show complete information
            info_result = get_pincode_info(pincode) if not data_file else PincodeData(data_file).get_pincode_info(pincode)
            output_result(info_result, args.json, args.verbose, f"Complete information for {pincode}")
    
    except Exception as e:
        raise e


def handle_nearby_command(pincode: str, radius_km: float, limit: int, json_output: bool, verbose: bool, data_file: Optional[str] = None) -> None:
    """Handle the 'nearby' geospatial command."""
    try:
        result = get_nearby_pincodes(pincode, radius_km, limit)
        
        if not result:
            print(f"No pincodes found within {radius_km}km of {pincode}")
            return
        
        title = f"Pincodes within {radius_km}km of {pincode} ({len(result)} found)"
        output_result(result, json_output, verbose, title)
    
    except Exception as e:
        raise e


def handle_nearest_command(latitude: float, longitude: float, limit: int, json_output: bool, verbose: bool) -> None:
    """Handle the 'nearest' geospatial command."""
    try:
        result = get_nearest_pincodes(latitude, longitude, limit)
        
        if not result:
            print(f"No pincodes found near coordinates ({latitude}, {longitude})")
            return
        
        title = f"Nearest pincodes to ({latitude}, {longitude}) ({len(result)} found)"
        output_result(result, json_output, verbose, title)
    
    except Exception as e:
        raise e


def search_state(state_name: str, json_output: bool, verbose: bool, data_file: Optional[str] = None) -> None:
    """Search pincodes by state name."""
    try:
        if not data_file:
            result = search_by_state(state_name)
        else:
            result = PincodeData(data_file).search_by_state(state_name)
        
        if not result:
            print(f"No pincodes found for state: {state_name}")
            return
        
        output_result(result, json_output, verbose, f"Pincodes in {state_name} ({len(result)} found)")
    
    except Exception as e:
        raise e


def search_district(district_name: str, state_name: Optional[str], json_output: bool, verbose: bool, data_file: Optional[str] = None) -> None:
    """Search pincodes by district name."""
    try:
        if not data_file:
            result = search_by_district(district_name, state_name)
        else:
            result = PincodeData(data_file).search_by_district(district_name, state_name)
        
        if not result:
            location = f"{district_name}" + (f" in {state_name}" if state_name else "")
            print(f"No pincodes found for district: {location}")
            return
        
        location = f"{district_name}" + (f", {state_name}" if state_name else "")
        output_result(result, json_output, verbose, f"Pincodes in {location} ({len(result)} found)")
    
    except Exception as e:
        raise e


def list_states(json_output: bool, verbose: bool) -> None:
    """List all states in the dataset."""
    try:
        result = get_states()
        output_result(result, json_output, verbose, f"All states ({len(result)} found)")
    
    except Exception as e:
        raise e


def list_districts(state_name: Optional[str], json_output: bool, verbose: bool) -> None:
    """List all districts, optionally filtered by state."""
    try:
        result = get_districts(state_name)
        
        if state_name:
            title = f"Districts in {state_name} ({len(result)} found)"
        else:
            title = f"All districts ({len(result)} found)"
        
        output_result(result, json_output, verbose, title)
    
    except Exception as e:
        raise e


def show_statistics(json_output: bool, verbose: bool, data_file: Optional[str] = None) -> None:
    """Show dataset statistics."""
    try:
        if not data_file:
            from .core import _get_default_instance
            stats = _get_default_instance().get_statistics()
        else:
            stats = PincodeData(data_file).get_statistics()
        
        output_result(stats, json_output, verbose, "Dataset Statistics")
    
    except Exception as e:
        raise e


def output_result(result: Any, json_output: bool, verbose: bool, title: Optional[str] = None) -> None:
    """Output result in the specified format."""
    if json_output:
        if title and verbose:
            output = {"title": title, "data": result}
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if title and verbose:
            print(f"\n{title}:")
            print("=" * len(title))
        
        if isinstance(result, list):
            if len(result) == 0:
                print("No results found.")
            elif isinstance(result[0], dict):
                # Pretty print list of dictionaries
                for i, item in enumerate(result, 1):
                    if verbose and len(result) > 1:
                        print(f"\n{i}. Record:")
                        print("-" * 10)
                    for key, value in item.items():
                        print(f"{key.replace('_', ' ').title()}: {value}")
                    if not verbose and i < len(result):
                        print()
            else:
                # Simple list
                for item in result:
                    print(item)
        
        elif isinstance(result, dict):
            # Pretty print dictionary
            for key, value in result.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        else:
            # Simple value
            print(result)


if __name__ == "__main__":
    main()
