import argparse
import sys
import os

# Ensure the root directory is in the path to import submodules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.LawDataScraper import main as run_scraper
from retriever.build_db import build_vector_database
from retriever.search import SaudiLawRetriever
from api.rag import SaudiLawRAG

def print_logo():
    logo = r"""
  ____                  _ _   _                     ____      _    ____ 
 / ___|  __ _ _   _  __| (_) | |    __ ___      __ |  _ \    / \  / ___|
 \___ \ / _` | | | |/ _` | | | |   / _` \ \ /\ / / | |_) |  / _ \ | |  _ 
  ___) | (_| | |_| | (_| | | | |__| (_| |\ V  V /  |  _ <  / ___ \| |_| |
 |____/ \__,_|\__,_|\__,_|_| |_____\__,_| \_/\_/   |_| \_\/_/   \_\____|
    """
    print(logo)
    print("="*69)
    print("          Central Control Interface - Ministry of Justice")
    print("="*69 + "\n")

def interactive_menu():
    print_logo()
    while True:
        print("Please Select an Operation:")
        print("  [1] 📥 Scrape Law Data (Ministry of Justice API)")
        print("  [2] 🗄️  Build/Update Vector Database (PostgreSQL)")
        print("  [3] 🔍 Test Semantic Search (Retrieval Only)")
        print("  [4] 🤖 Chat with ALLaM (Full RAG)")
        print("  [5] ❌ Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            force_input = input("Force overwrite existing files? (y/N): ").strip().lower()
            force = force_input == 'y'
            serial = input("Target specific serial ID? (Press Enter for all): ").strip()
            print(f"\nStarting Scraper... (Force Update: {force})")
            run_scraper(force_update=force, target_serial=serial if serial else None)
            print("\nScraping complete!")
            
        elif choice == "2":
            print("\nStarting Database Builder...")
            print("Note: This is safe to run multiple times. Existing vectors will be updated.")
            build_vector_database()
            print("\nDatabase sync complete!")
            
        elif choice == "3":
            query = input("\nEnter your Arabic search query: ").strip()
            if not query:
                print("Query cannot be empty.")
                continue
            top_input = input("Number of results (default 3): ").strip()
            top_k = int(top_input) if top_input.isdigit() else 3
            
            print(f"\nSearching Database for: {query}")
            try:
                retriever = SaudiLawRetriever()
                results = retriever.search(query, top_k=top_k)
                for i, res in enumerate(results):
                    print(f"\n--- النتيجة {i+1} ---")
                    print(f"القانون: {res['law_name']}")
                    print(f"مسار المادة: {' > '.join(res['hierarchy'])}")
                    print(f"النص: {res['text'][:300]}...")
                    print(f"قوة المطابقة: {res['score']:.4f}")
            except Exception as e:
                print(f"Search error: {e}")
                
        elif choice == "4":
            print("\n" + "="*50)
            print("🤖 Starting ALLaM Chat Session (Type 'exit' to leave)")
            print("="*50)
            
            try:
                rag = SaudiLawRAG()
                while True:
                    query = input("\n[أنت / You]: ").strip()
                    if query.lower() == 'exit':
                        print("Ending chat session...")
                        break
                    
                    if not query:
                        continue
                    
                    print(f"\n[ALLaM]: ", end="")
                    # The stream will output directly here
                    answer, sources = rag.generate_answer(query, top_k=3)
                    
                    # Optionally print sources
                    # show_sources = input("\nShow exact sources used? (y/N): ").strip().lower()
                    # if show_sources == 'y':
                    #     for i, res in enumerate(sources):
                    #         print(f"\n[المصدر {i+1}]: {res['law_name']} > {' > '.join(res['hierarchy'])}")
            except Exception as e:
                print(f"RAG Chat Error: {e}")
                
        elif choice == "5":
            print("Exiting Saudi Law RAG Management CLI. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please select 1, 2, 3, 4, or 5.")
        
        print("\n" + "-"*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Saudi Law RAG Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape law data from Ministry of Justice")
    scrape_parser.add_argument("--force", action="store_true", help="Force overwrite existing downloaded JSON files")
    scrape_parser.add_argument("--serial", type=str, help="Scrape a specific law by its Serial ID")

    # Build DB command
    build_parser = subparsers.add_parser("build-db", help="Build/Update the PostgreSQL Vector Database")

    # Search command
    search_parser = subparsers.add_parser("search", help="Test semantic search")
    search_parser.add_argument("query", type=str, help="The Arabic question to search for")
    search_parser.add_argument("--top", type=int, default=3, help="Number of results to return")

    # If no arguments provided, launch interactive menu
    if len(sys.argv) == 1:
        interactive_menu()
        return

    args = parser.parse_args()

    if args.command == "scrape":
        print(f"Starting Scraper... (Force Update: {args.force})")
        run_scraper(force_update=args.force, target_serial=args.serial)
        
    elif args.command == "build-db":
        print("Starting Database Builder...")
        print("Note: This is safe to run multiple times! Existing vectors will be updated, not duplicated.")
        build_vector_database()
        
    elif args.command == "search":
        print(f"Searching Database for: {args.query}")
        retriever = SaudiLawRetriever()
        results = retriever.search(args.query, top_k=args.top)
        
        for i, res in enumerate(results):
            print(f"\n--- النتيجة {i+1} ---")
            print(f"القانون: {res['law_name']}")
            print(f"مسار المادة: {' > '.join(res['hierarchy'])}")
            print(f"النص: {res['text'][:300]}...")
            print(f"قوة المطابقة: {res['score']:.4f}")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()