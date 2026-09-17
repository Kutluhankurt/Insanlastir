"""Fonetik / konuşma dili yazımı (Bölüm 4).

Yüklem çekimlerindeki fonetik indirgemeler (geliyorum->geliyom,
yapacağım->yapıcam) zaten predicate_rules.py'de ünlü uyumuyla ele
alınıyor; bu modül aynı mantığı tekrar etmemek için oradaki
fonksiyonları yeniden dışa aktarır.
"""
from app.error_engine.predicate_rules import (  # noqa: F401
    TransformResult,
    apply_first_matching,
    transform_future_1pl,
    transform_future_1sg,
    transform_yor,
)
