import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from litellm import models_by_provider

ENV_FILE = ".env"

# Provider ka naam → .env variable ka naam
PROVIDER_ENV_MAP = {
    "openai":       "OPENAI_API_KEY",
    "gemini":       "GEMINI_API_KEY",
    "anthropic":    "ANTHROPIC_API_KEY",
    "groq":         "GROQ_API_KEY",
    "mistral":      "MISTRAL_API_KEY",
    "openrouter":   "OPENROUTER_API_KEY",
    "huggingface":  "HUGGINGFACE_API_KEY",
    "cloudflare":   "CLOUDFLARE_API_KEY",
    "zhipuai":      "ZHIPUAI_API_KEY",
    "cohere":       "COHERE_API_KEY",
    "xai":          "XAI_API_KEY",
    "deepseek":     "DEEPSEEK_API_KEY",
    "together_ai":  "TOGETHERAI_API_KEY",
    "ai21":         "AI21_API_KEY",
    "voyage":       "VOYAGE_API_KEY",
    "replicate":    "REPLICATE_API_KEY",
}


def list_available_providers():
    """LiteLLM ke saare supported providers dikhata hai"""
    providers = sorted(models_by_provider.keys())
    print("\n📋 Available Providers:")
    for i, p in enumerate(providers, 1):
        print(f"   {i}. {p}")
    return providers


def save_key_to_env(env_var: str, api_key: str):
    """API key ko .env mein save/update karta hai"""
    # Agar .env file nahi hai to bana dein
    if not Path(ENV_FILE).exists():
        Path(ENV_FILE).touch()

    # Key save karein (agar pehle se hai to overwrite ho jayegi)
    set_key(ENV_FILE, env_var, api_key)
    print(f"✅ Key save ho gayi: {env_var} → {ENV_FILE}")


def show_models(provider: str):
    """Provider ke saare models ki list dikhata hai"""
    # LiteLLM mein provider ka naam match karein
    provider_key = None
    for k in models_by_provider.keys():
        if k.lower() == provider.lower():
            provider_key = k
            break

    if not provider_key:
        print(f"⚠️  '{provider}' ke models LiteLLM mein nahi mile.")
        print("   Shayad provider ka naam spelling galat hai.")
        return

    models = models_by_provider.get(provider_key, [])
    print(f"\n📋 {provider.upper()} ke {len(models)} models:\n")
    for m in models:
        print(f"   • {m}")
    print()


def main():
    print("=" * 60)
    print("   🤖 AI Provider Setup — Models Explorer")
    print("=" * 60)

    # 1) Provider ka naam poochein
    show_help = input("\n❓ Providers ki list dekhni hai? (y/n): ").strip().lower()
    if show_help == "y":
        list_available_providers()

    provider = input("\n🔹 Provider ka naam likhein (e.g. openai, gemini, groq): ").strip().lower()

    if not provider:
        print("❌ Provider ka naam khali nahi ho sakta.")
        return

    # 2) API key poochein
    api_key = input(f"🔑 {provider.upper()} ki API Key daalein: ").strip()

    if not api_key:
        print("❌ API key khali nahi ho sakti.")
        return

    # 3) .env variable ka naam dhoondein
    env_var = PROVIDER_ENV_MAP.get(provider)

    if not env_var:
        # Agar mapping mein nahi hai to automatic bana dein
        env_var = provider.upper().replace("-", "_") + "_API_KEY"
        print(f"⚠️  '{provider}' mapping mein nahi tha, lekin yeh naam use karenge: {env_var}")

    # 4) Key save karein
    save_key_to_env(env_var, api_key)

    # 5) Environment mein bhi load karein (is session ke liye)
    os.environ[env_var] = api_key

    # 6) Models dikhaein
    show_models(provider)

    print("=" * 60)
    print("✅ Kaam mukammal! Aap dobara chala kar doosra provider add kar sakte hain.")
    print("=" * 60)


if __name__ == "__main__":
    main()