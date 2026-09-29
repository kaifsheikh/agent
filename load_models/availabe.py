import os
from pathlib import Path
from litellm import models_by_provider

ENV_FILE = ".env"


def load_env_keys():
    keys = {}
    if not Path(ENV_FILE).exists():
        print(f"{ENV_FILE} .env not found.")
        return keys

    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                keys[k.strip()] = v.strip().strip("'").strip('"')
    return keys


def generate_env_var_name(provider: str) -> str:
    return provider.upper().replace("-", "_") + "_API_KEY"


def get_active_providers():
    """Sirf woh providers jin ki key .env mein hai"""
    env_keys = load_env_keys()
    active = []

    for provider in sorted(models_by_provider.keys()):
        env_var = generate_env_var_name(provider)
        if env_var in env_keys:
            models = models_by_provider.get(provider, [])
            if models:
                active.append({
                    "provider": provider,
                    "env_var": env_var,
                    "models": models,
                    "key": env_keys[env_var],
                })
    return active


def show_summary(active):
    """Total providers aur models ka summary"""
    total_models = sum(len(p["models"]) for p in active)

    print("=" * 60)
    print("   📊 SUMMARY")
    print("=" * 60)
    print(f"   🧩 Total Providers Active : {len(active)}")
    print(f"   🤖 Total Models Available : {total_models}")
    print("=" * 60)


def show_provider_menu(active):
    """Numbered list of providers"""
    print("\n   📋 Providers List:")
    print("-" * 60)
    for i, p in enumerate(active, 1):
        masked = p["key"][:6] + "..." + p["key"][-4:] if len(p["key"]) > 10 else "***"
        print(f"   {i:>3}. {p['provider']:<20} ({len(p['models'])} models)  {masked}")
    print("-" * 60)


def show_models(provider_info):
    """Ek provider ke saare models dikhata hai"""
    provider = provider_info["provider"]
    models = provider_info["models"]

    print("\n" + "=" * 60)
    print(f"   📋 {provider.upper()} — {len(models)} models")
    print("=" * 60)
    for m in models:
        print(f"   • {m}")
    print("=" * 60)


def main():
    active = get_active_providers()

    if not active:
        print("⚠️  Aap ke .env mein koi valid provider key nahi mili.")
        return

    # Summary + providers list
    show_summary(active)
    show_provider_menu(active)

    # Loop — user bar bar number daal kar models dekh sakta hai
    while True:
        choice = input("\n🔹 Provider ka number daalein (ya 'q' quit ke liye): ").strip().lower()

        if choice == "q":
            print("👋 Bye!")
            break

        if not choice.isdigit():
            print("❌ Sirf number daalein (ya 'q' quit ke liye).")
            continue

        idx = int(choice)
        if idx < 1 or idx > len(active):
            print(f"❌ Galat number. 1 se {len(active)} ke darmiyan daalein.")
            continue

        show_models(active[idx - 1])


if __name__ == "__main__":
    main()