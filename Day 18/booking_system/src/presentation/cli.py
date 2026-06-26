import argparse

from src.application.services import HotelService, create_test_data


def main():
    parser = argparse.ArgumentParser(description="Hotel Management CLI")
    parser.add_argument("--search", help="Search hotels by city")
    parser.add_argument("--min-rating", type=float, help="Minimum rating")
    parser.add_argument("--list", action="store_true", help="List all hotels")

    args = parser.parse_args()
    service = create_test_data()

    if args.search:
        results = service.search_hotels(city=args.search, min_rating=args.min_rating)
        print(f"Found {len(results)} hotels:")
        for h in results:
            print(f"  - {h.name} ({h.city}) - Rating: {h.rating}")

    elif args.list:
        for hotel in service._hotels.values():
            print(f"{hotel.id}. {hotel.name} ({hotel.city}) - Rating: {hotel.rating}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
