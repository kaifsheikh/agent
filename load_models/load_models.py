import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from litellm import models_by_provider

ENV_FILE = ".env"


def get_litellm_providers():
    """LiteLLM ke saare supported providers ki list return karta hai"""
    return sorted(models_by_provider.keys())


def list_available_providers():
    """LiteLLM ke saare supported providers dikhata hai (numbered)"""
    providers = get_litellm_providers()
    print("\n📋 LiteLLM Supported Providers:")
    print("-" * 60)
    for i, p in enumerate(providers, 1):
        print(f"   {i:>3}. {p}")
    print("-" * 60)
    print(f"   Total: {len(providers)} providers\n")
    return providers


def resolve_provider(user_input: str):
    """
    User ke input ko LiteLLM ke exact provider naam se match karta hai.
    Match mila to exact naam return karega, warna None.
    """
    providers = get_litellm_providers()

    # Case-insensitive exact match
    for p in providers:
        if p.lower() == user_input.lower():
            return p

    # Koi match nahi mila
    return None


def suggest_similar(user_input: str, limit: int = 5):
    """Agar exact match na mile to milte-julte naam suggest karta hai"""
    providers = get_litellm_providers()
    q = user_input.lower()
    matches = [p for p in providers if q in p.lower()]
    return matches[:limit]


def generate_env_var_name(provider: str) -> str:
    """
    Provider ke naam se .env variable ka naam auto banata hai.
    Example: "openai" → "OPENAI_API_KEY"
             "together_ai" → "TOGETHER_AI_API_KEY"
             "xai" → "XAI_API_KEY"
    """
    return provider.upper().replace("-", "_") + "_API_KEY"



def save_key_to_env(env_var: str, api_key: str):
    """API key ko .env mein save/update karta hai"""
    if not Path(ENV_FILE).exists():
        Path(ENV_FILE).touch()

    set_key(ENV_FILE, env_var, api_key)
    print(f"✅ Key save ho gayi: {env_var} → {ENV_FILE}")


def show_models(provider: str):
    """Provider ke saare models ki list dikhata hai"""
    models = models_by_provider.get(provider, [])
    if not models:
        print(f"⚠️  '{provider}' ke koi models nahi mile.")
        return

    print(f"\n📋 {provider.upper()} ke {len(models)} models:\n")
    for m in models:
        print(f"   • {m}")
    print()


def main():
    print("=" * 60)
    print("   🤖 AI Provider Setup — Models Explorer")
    print("=" * 60)

    # 1) Providers ki list dikhane ka option
    show_help = input("\n❓ Providers ki list dekhni hai? (y/n): ").strip().lower()
    if show_help == "y":
        list_available_providers()

    # 2) Provider ka naam poochein
    provider_input = input("🔹 Provider ka naam likhein (e.g. openai, gemini, groq): ").strip()

    if not provider_input:
        print("❌ Provider ka naam khali nahi ho sakta.")
        return

    # 3) LiteLLM mein provider validate karein
    provider = resolve_provider(provider_input)

    if not provider:
        print(f"\n❌ '{provider_input}' provider LiteLLM mein available NAHI hai.")
        similar = suggest_similar(provider_input)
        if similar:
            print(f"   💡 Shayad aap yeh chahte the: {', '.join(similar)}")
        else:
            print("   💡 'y' likh kar saari providers ki list dekh lein.")
        return

    print(f"✅ Provider mila: {provider}")

    # 4) API key poochein
    api_key = input(f"🔑 {provider.upper()} ki API Key daalein: ").strip()

    if not api_key:
        print("❌ API key khali nahi ho sakti.")
        return

    # 5) .env variable ka naam AUTO generate karein
    env_var = generate_env_var_name(provider)
    print(f"📝 Env variable naam (auto): {env_var}")

    # 6) Key save karein
    save_key_to_env(env_var, api_key)

    # 7) Environment mein bhi load karein (is session ke liye)
    os.environ[env_var] = api_key

    # 8) Models dikhaein
    show_models(provider)

    print("=" * 60)
    print("✅ Kaam mukammal! Aap dobara chala kar doosra provider add kar sakte hain.")
    print("=" * 60)


if __name__ == "__main__":
    main()