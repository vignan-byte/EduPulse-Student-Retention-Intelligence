"""CLI to bootstrap local fictional-case users without hardcoded passwords."""
import argparse
import getpass
from src.case_store import DemoCaseStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--role", choices=["admin", "advisor"], required=True)
    parser.add_argument("--actor", help="Existing administrator username (for subsequent users)")
    parser.add_argument("--database", default="local_demo/cases.sqlite3")
    args = parser.parse_args()
    password = getpass.getpass("New password (12+ characters): ")
    actor_password = getpass.getpass("Administrator password: ") if args.actor else None
    DemoCaseStore(args.database).create_user(args.username, password, args.role,
                                               actor=args.actor, actor_password=actor_password)
    print(f"Created {args.role}: {args.username}")


if __name__ == "__main__":
    main()
