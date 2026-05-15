"""
Reply templates for the most common buyer questions on Vinted.

Claude uses list_reply_templates() to see what's available, picks the one that
matches the incoming message, fills the placeholders, and either drafts a reply
or sends it via send_message.

Tweak the wording here to match your friend's voice.
"""

from __future__ import annotations

from typing import Any


# Each template has:
#   id          : stable key Claude can refer to
#   intent      : what kind of question this answers
#   triggers    : keywords/phrases that suggest this template fits (FR)
#   text        : the reply, with {placeholders}
#   placeholders: human description of each placeholder
#   safe_auto   : True if it's reasonable to send this without human review

TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "still_available_yes",
        "intent": "Acheteur demande si l'article est toujours dispo — réponse: oui",
        "triggers": ["toujours dispo", "encore dispo", "still available", "disponible"],
        "text": "Bonjour ! Oui, c'est toujours disponible 🙂",
        "placeholders": {},
        "safe_auto": True,
    },
    {
        "id": "still_available_no",
        "intent": "Acheteur demande si dispo — réponse: déjà réservé/vendu",
        "triggers": ["toujours dispo", "encore dispo"],
        "text": "Bonjour ! Désolé, l'article vient d'être {status} 😕",
        "placeholders": {"status": "réservé / vendu"},
        "safe_auto": False,
    },
    {
        "id": "measurements",
        "intent": "Acheteur demande des mesures précises",
        "triggers": ["mesures", "dimensions", "longueur", "largeur", "épaules", "manches"],
        "text": (
            "Bonjour ! Les mesures à plat : {measurements}. "
            "Dis-moi si tu veux que je remesure un endroit précis."
        ),
        "placeholders": {"measurements": "p.ex. 'longueur 70cm, largeur 50cm'"},
        "safe_auto": False,
    },
    {
        "id": "condition",
        "intent": "Acheteur demande l'état réel / défauts",
        "triggers": ["état", "défaut", "tache", "trou", "porté", "abimé", "abîmé"],
        "text": (
            "Bonjour ! L'article est en {condition}. {details} "
            "Je peux t'envoyer des photos supplémentaires si tu veux."
        ),
        "placeholders": {
            "condition": "p.ex. 'très bon état'",
            "details": "p.ex. 'Aucun défaut visible.' ou 'Petite tache sur la manche gauche.'",
        },
        "safe_auto": False,
    },
    {
        "id": "shipping_time",
        "intent": "Acheteur demande quand l'envoi sera fait",
        "triggers": ["envoi", "expédition", "quand", "délai", "rapide"],
        "text": (
            "Bonjour ! J'envoie sous {delay} après réception du paiement. "
            "Bonne journée 🙂"
        ),
        "placeholders": {"delay": "p.ex. '24h' ou '2 jours ouvrés'"},
        "safe_auto": True,
    },
    {
        "id": "bundle_discount",
        "intent": "Acheteur veut un lot / réduction multi-articles",
        "triggers": ["lot", "plusieurs articles", "réduction", "bundle", "remise"],
        "text": (
            "Bonjour ! Pas de souci, ajoute les articles à ton panier et "
            "fais-moi une offre groupée via Vinted — je regarde et je te réponds."
        ),
        "placeholders": {},
        "safe_auto": True,
    },
    {
        "id": "price_negotiation_polite_decline",
        "intent": "Acheteur propose un prix trop bas — refus poli",
        "triggers": ["offre", "prix", "moins cher", "négo", "négociable"],
        "text": (
            "Bonjour ! Merci pour ton offre. Je suis déjà au plus bas, je ne peux "
            "pas descendre en dessous de {min_price}€ pour cet article. "
            "Dis-moi si ça te va 🙂"
        ),
        "placeholders": {"min_price": "p.ex. '15'"},
        "safe_auto": False,
    },
    {
        "id": "size_question",
        "intent": "Acheteur demande des conseils de taille",
        "triggers": ["taille", "size", "ça taille", "petit", "grand"],
        "text": (
            "Bonjour ! D'expérience, {sizing_advice}. "
            "Si tu hésites, je peux te donner les mesures à plat."
        ),
        "placeholders": {"sizing_advice": "p.ex. 'ça taille normalement' ou 'plutôt petit, prendre une taille au-dessus'"},
        "safe_auto": False,
    },
    {
        "id": "thanks_after_purchase",
        "intent": "Acheteur vient d'acheter — remerciement",
        "triggers": ["achat", "acheté", "merci", "paiement"],
        "text": (
            "Merci pour ton achat ! J'envoie ça {delay}. "
            "Bonne réception 📦"
        ),
        "placeholders": {"delay": "p.ex. 'demain matin'"},
        "safe_auto": True,
    },
]


def get_template(template_id: str) -> dict[str, Any] | None:
    for t in TEMPLATES:
        if t["id"] == template_id:
            return t
    return None
