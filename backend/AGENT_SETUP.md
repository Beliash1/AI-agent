# Cici Agent — დამატების ინსტრუქცია

## 1. ფაილების მდებარეობა (ზუსტად შენი სტრუქტურის მიხედვით)

```
backend/
├── tools/
│   ├── web_tool.py      ← ახალი
│   └── code_tool.py     ← ახალი
├── core/
│   └── orchestrator.py  ← ახალი
└── api/
    └── agent_routes.py  ← ახალი
```

უბრალოდ ჩააგდე ეს 4 ფაილი შესაბამის ფოლდერებში — არაფერს არსებულს არ ეხება
(`services/ollama.py`, `routes.py` და ა.შ. უცვლელი რჩება).

## 2. დამოკიდებულებები

```bash
pip install httpx beautifulsoup4 --break-system-packages
```

(httpx შენ უკვე გაქვს, ასე რომ მხოლოდ beautifulsoup4-ია ახალი)

## 3. main.py-ში ჩართვა

`agent_routes.py`-ის ბოლოში მითითებული 2 ხაზი დაამატე შენს `main.py`-ში,
routes.py-ის ჩართვის გვერდით:

```python
from api.agent_routes import router as agent_router
app.include_router(agent_router)
```

## 4. შემოწმება

გაუშვი სერვერი ჩვეულებრივად:
```bash
python -m uvicorn backend.main:app --reload
```

გახსენი http://127.0.0.1:8000/docs — გამოჩნდება ახალი **POST /agent**.

მაგალითი request body:
```json
{"message": "მოძებნე დღევანდელი ვალუტის კურსი და დამითვალე 100 დოლარი ლარში"}
```

აგენტი ავტომატურად:
1. გამოიძახებს web_search-ს კურსის საპოვნელად
2. თუ საჭიროა, გაუშვებს კოდს გამოსათვლელად (თვითშემოწმებით, თუ შეცდომაა)
3. დააბრუნებს საბოლოო პასუხს რეალურ მონაცემებზე დაყრდნობით

## 5. მნიშვნელოვანი შენიშვნები

- **timeout**: `code_tool.py`-ში კოდის შესრულებას 10 წამიანი ლიმიტი აქვს
  (`TIMEOUT_SECONDS`) — თუ გაინტერესებს უფრო მძიმე გამოთვლები, გაზარდე.
- **უსაფრთხოება**: `run_python_code` აწარმოებს კოდს subprocess-ში, მაგრამ
  სრული sandbox არ არის (არ არის დაცული ფაილურ სისტემაზე წვდომისგან). თუ
  production-ში წაიღებ, დაამატე docker-ში იზოლირებული კონტეინერი ან
  restricted user.
- **MAX_STEPS / MAX_RETRIES**: orchestrator.py-ში 5 ნაბიჯი, code_tool.py-ში
  3 მცდელობაა თვითშესწორებისთვის — შეგიძლია გაზარდო/შეამციროთ საჭიროებისამებრ.
- **მოდელი**: ნაგულისხმევად `qwen3:4b`-ს იყენებს (შენი უკვე გადმოწერილი
  მოდელია) — request body-ში `model` ველით შეგიძლია სხვა მოდელზეც გადართო.
