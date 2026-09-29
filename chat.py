import os
import sys
from pathlib import Path
from litellm import completion, models_by_provider

# .env file ka sahi path — chat.py ke folder ke andar load_models mein hai
ENV_FILE = Path(__file__).parent / "load_models" / ".env"


# ---------------- ENV LOADER ----------------
def load_env_keys():
    """Sirf .env file se keys padhta hai (quotes strip karta hai)"""
    keys = {}
    if not ENV_FILE.exists():
        print(f"❌ {ENV_FILE} file nahi mili.")
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
    """Provider naam → env var naam (always _API_KEY suffix)"""
    return provider.upper().replace("-", "_") + "_API_KEY"


# ---------------- PROVIDER / MODEL LIST ----------------
def get_active_providers():
    """Sirf woh providers jinki key .env mein hai"""
    env_keys = load_env_keys()
    active = []

    for provider in sorted(models_by_provider.keys()):
        env_var = generate_env_var_name(provider)
        if env_var in env_keys:
            # >>> sorted() + set() se list banayein <<<
            models = sorted(models_by_provider.get(provider, set()))
            if models:
                active.append({
                    "provider": provider,
                    "models": models,
                })
    return active


def show_providers(active):
    """Providers ki numbered list"""
    print("\n" + "=" * 60)
    print("   📋 Available Providers")
    print("=" * 60)
    for i, p in enumerate(active, 1):
        print(f"   [{i}] {p['provider']:<20} ({len(p['models'])} models)")
    print("=" * 60)


def show_models(provider_info):
    """Ek provider ke numbered models"""
    provider = provider_info["provider"]
    models = provider_info["models"]

    print("\n" + "=" * 60)
    print(f"   📋 {provider.upper()} — {len(models)} models")
    print("=" * 60)
    for i, m in enumerate(models, 1):
        print(f"   [{i}] {m}")
    print("=" * 60)


# ---------------- SELECTION ----------------
def pick_provider(active):
    """User se provider choose karwata hai"""
    while True:
        show_providers(active)
        choice = input("\n🔹 Provider ka number daalein (ya 'q' quit): ").strip().lower()

        if choice == "q":
            return None
        if not choice.isdigit():
            print("❌ Sirf number daalein.")
            continue

        idx = int(choice)
        if idx < 1 or idx > len(active):
            print(f"❌ Galat number. 1 se {len(active)} ke darmiyan.")
            continue

        return active[idx - 1]


def pick_model(provider_info):
    """User se model choose karwata hai"""
    while True:
        show_models(provider_info)
        choice = input("\n🔹 Model ka number daalein (ya 'b' back): ").strip().lower()

        if choice == "b":
            return None
        if not choice.isdigit():
            print("❌ Sirf number daalein.")
            continue

        idx = int(choice)
        models = provider_info["models"]
        if idx < 1 or idx > len(models):
            print(f"❌ Galat number. 1 se {len(models)} ke darmiyan.")
            continue

        return models[idx - 1]


# ---------------- CHAT ----------------
def chat_loop(model: str):
    """Simple chat loop"""
    print("\n" + "=" * 60)
    print(f"   💬 Chat Started — {model}")
    print("   Commands: 'm' = change model | 'p' = change provider | 'q' = quit")
    print("=" * 60)

    while True:
        try:
            prompt = input("\n>>> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Bye!")
            return "quit"

        if not prompt:
            continue

        cmd = prompt.lower()

        if cmd == "q":
            print("👋 Bye!")
            return "quit"
        if cmd == "m":
            return "change_model"
        if cmd == "p":
            return "change_provider"

        # AI ko bhejo
        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            print(f"\n🤖 ({model}):")
            print(response.choices[0].message.content)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("   (Prompt dobara try karein ya model change karein)")


# ---------------- MAIN ----------------
def main():
    # .env file se keys load karein taake LiteLLM khud use kar sake
    env_keys = load_env_keys()
    for k, v in env_keys.items():
        os.environ[k] = v

    active = get_active_providers()

    if not active:
        print("⚠️  Aap ke .env mein koi valid provider key nahi mili.")
        print(f"   Check karein: {ENV_FILE}")
        return

    provider_info = None
    selected_model = None

    while True:
        if provider_info is None:
            provider_info = pick_provider(active)
            if provider_info is None:
                print("👋 Bye!")
                return

        if selected_model is None:
            selected_model = pick_model(provider_info)
            if selected_model is None:
                provider_info = None
                continue

        action = chat_loop(selected_model)

        if action == "quit":
            return
        elif action == "change_model":
            selected_model = None
        elif action == "change_provider":
            provider_info = None
            selected_model = None


if __name__ == "__main__":
    main()