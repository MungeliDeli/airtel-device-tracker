# MongoDB Atlas — Seed Data

## How to Insert

1. Go to your **MongoDB Atlas** dashboard
2. Click **Browse Collections** → `airtel_tracker_db`
3. For each collection below, click **Insert Document**, switch to the **Array** tab, and paste the full JSON array

---

## Collection: `users` (Supervisors)

Paste this entire array into the `users` collection.  
Default password for all supervisors is: **`changeme123`** (admin should update these after first login).

```json
[
  {
    "username": "kelvin.kapupula",
    "password_hash": "changeme123",
    "role": "supervisor",
    "shop_name": "HQ"
  },
  {
    "username": "victor.zembo",
    "password_hash": "changeme123",
    "role": "supervisor",
    "shop_name": "East Park"
  },
  {
    "username": "joseph.nkhoma",
    "password_hash": "changeme123",
    "role": "supervisor",
    "shop_name": "Cosmopolitan"
  },
  {
    "username": "victor.kayombo",
    "password_hash": "changeme123",
    "role": "supervisor",
    "shop_name": "Crossroads"
  },
  {
    "username": "daniel.chalwe",
    "password_hash": "changeme123",
    "role": "supervisor",
    "shop_name": "Arcades"
  },
  {
    "username": "gibson.nkole",
    "password_hash": "changeme123",
    "role": "supervisor",
    "shop_name": "Chalala"
  }
]
```

---

## Collection: `installers`

Paste this entire array into the `installers` collection.

```json
[
  { "name": "Panga Mvewa",          "cug_number": "978982272", "supervisor_username": "kelvin.kapupula" },
  { "name": "Alex Muyale",          "cug_number": "978982043", "supervisor_username": "kelvin.kapupula" },
  { "name": "Aaron Phiri",          "cug_number": "978982413", "supervisor_username": "kelvin.kapupula" },
  { "name": "Deborah Daka",         "cug_number": "978982310", "supervisor_username": "kelvin.kapupula" },
  { "name": "Siyambango Mundia",    "cug_number": "978982739", "supervisor_username": "kelvin.kapupula" },
  { "name": "Japhet Nyirenda",      "cug_number": "978982238", "supervisor_username": "kelvin.kapupula" },
  { "name": "John Muliya",          "cug_number": "978982023", "supervisor_username": "kelvin.kapupula" },
  { "name": "Stephen B Nyirenda",   "cug_number": "978982281", "supervisor_username": "kelvin.kapupula" },
  { "name": "Matandiko Lawrence",   "cug_number": "978982563", "supervisor_username": "kelvin.kapupula" },
  { "name": "Leonard J Kachumi",    "cug_number": "978982104", "supervisor_username": "kelvin.kapupula" },
  { "name": "Emmanuel Chansa",      "cug_number": "978982082", "supervisor_username": "kelvin.kapupula" },
  { "name": "Clive Munyama",        "cug_number": "978982897", "supervisor_username": "kelvin.kapupula" },
  { "name": "Trevor Mufaya",        "cug_number": "978982902", "supervisor_username": "kelvin.kapupula" },
  { "name": "Cubo Chime",           "cug_number": "978982935", "supervisor_username": "kelvin.kapupula" },
  { "name": "Chillya Chulu",        "cug_number": "978982919", "supervisor_username": "kelvin.kapupula" },
  { "name": "Goodson Mumbelunga",   "cug_number": "978982567", "supervisor_username": "kelvin.kapupula" },

  { "name": "Isaac Chisale",        "cug_number": "978982884", "supervisor_username": "victor.zembo" },
  { "name": "David Zimba",          "cug_number": "978982024", "supervisor_username": "victor.zembo" },
  { "name": "Theresa Kabomba",      "cug_number": "978982556", "supervisor_username": "victor.zembo" },
  { "name": "Comfort Chapa",        "cug_number": "978982548", "supervisor_username": "victor.zembo" },
  { "name": "Mwape Chishala",       "cug_number": "978982608", "supervisor_username": "victor.zembo" },
  { "name": "Vincent Iyondo",       "cug_number": "978982430", "supervisor_username": "victor.zembo" },
  { "name": "Lubilo Hantambo",      "cug_number": "978982566", "supervisor_username": "victor.zembo" },
  { "name": "Kasonde Mukuka",       "cug_number": "978982664", "supervisor_username": "victor.zembo" },
  { "name": "Chinziwe Kasalwe",     "cug_number": "978982971", "supervisor_username": "victor.zembo" },
  { "name": "Alex Chanda",          "cug_number": "978982871", "supervisor_username": "victor.zembo" },
  { "name": "Fidelie Lubinda",      "cug_number": "978982917", "supervisor_username": "victor.zembo" },
  { "name": "Honest Mucheta",       "cug_number": "978982755", "supervisor_username": "victor.zembo" },
  { "name": "Ocean Mbiza",          "cug_number": "978982144", "supervisor_username": "victor.zembo" },
  { "name": "Mwape Chibwe",         "cug_number": "978982187", "supervisor_username": "victor.zembo" },

  { "name": "Happy Sumpa",          "cug_number": "978982213", "supervisor_username": "joseph.nkhoma" },
  { "name": "Chibaza Kapulo",       "cug_number": "978982634", "supervisor_username": "joseph.nkhoma" },
  { "name": "Mathias Parariza",     "cug_number": "978982488", "supervisor_username": "joseph.nkhoma" },
  { "name": "Dennis Malambo",       "cug_number": "978982497", "supervisor_username": "joseph.nkhoma" },
  { "name": "Harrison Mutale",      "cug_number": "978982159", "supervisor_username": "joseph.nkhoma" },
  { "name": "Lenario Malambo",      "cug_number": "978982664", "supervisor_username": "joseph.nkhoma" },
  { "name": "James Chola",          "cug_number": "978982825", "supervisor_username": "joseph.nkhoma" },
  { "name": "Paul Msambo",          "cug_number": "978982502", "supervisor_username": "joseph.nkhoma" },
  { "name": "Lupandu Masumba",      "cug_number": "978982644", "supervisor_username": "joseph.nkhoma" },
  { "name": "Susan Mofya",          "cug_number": "978982808", "supervisor_username": "joseph.nkhoma" },
  { "name": "Paul Mwenya",          "cug_number": "978982533", "supervisor_username": "joseph.nkhoma" },
  { "name": "Godfrey Bwalya",       "cug_number": "978982717", "supervisor_username": "joseph.nkhoma" },
  { "name": "Noreen Ngoma",         "cug_number": "978982875", "supervisor_username": "joseph.nkhoma" },
  { "name": "Blessings Mambusha",   "cug_number": "978982340", "supervisor_username": "joseph.nkhoma" },

  { "name": "Dickson Nkhowani",     "cug_number": "978982692", "supervisor_username": "victor.kayombo" },
  { "name": "Taonga Kalzinje",      "cug_number": "978982726", "supervisor_username": "victor.kayombo" },
  { "name": "Faith Selita Nambule", "cug_number": "978982443", "supervisor_username": "victor.kayombo" },
  { "name": "Mambow L Chilebela",   "cug_number": "978982204", "supervisor_username": "victor.kayombo" },
  { "name": "Hassan Phiri",         "cug_number": "978982913", "supervisor_username": "victor.kayombo" },
  { "name": "Elizabeth-Nelia Zulu", "cug_number": "978982986", "supervisor_username": "victor.kayombo" },
  { "name": "Nkweto Chiluba",       "cug_number": "978982290", "supervisor_username": "victor.kayombo" },
  { "name": "Malumbo Kunda",        "cug_number": "978982569", "supervisor_username": "victor.kayombo" },
  { "name": "Dabwiso Tembo",        "cug_number": "978982941", "supervisor_username": "victor.kayombo" },
  { "name": "Melvin Simpasa",       "cug_number": "978982241", "supervisor_username": "victor.kayombo" },
  { "name": "Museven Choonya",      "cug_number": "978982647", "supervisor_username": "victor.kayombo" },
  { "name": "Gilbert Nyirenda",     "cug_number": "978982517", "supervisor_username": "victor.kayombo" },

  { "name": "Li-David Mumba",       "cug_number": "978982901", "supervisor_username": "daniel.chalwe" },
  { "name": "Weston Daka",          "cug_number": "978982172", "supervisor_username": "daniel.chalwe" },
  { "name": "Karren Kamulosu",      "cug_number": "978982561", "supervisor_username": "daniel.chalwe" },
  { "name": "Reagan Makayi",        "cug_number": "978982985", "supervisor_username": "daniel.chalwe" },
  { "name": "Jonathan Chatila",     "cug_number": "978982922", "supervisor_username": "daniel.chalwe" },
  { "name": "Shadreck Soko",        "cug_number": "978982955", "supervisor_username": "daniel.chalwe" },
  { "name": "Constance Chilamo",    "cug_number": "978982611", "supervisor_username": "daniel.chalwe" },
  { "name": "Davy Mwansa",          "cug_number": "978982623", "supervisor_username": "daniel.chalwe" },
  { "name": "George Banda",         "cug_number": "978982926", "supervisor_username": "daniel.chalwe" },
  { "name": "Erick Halale",         "cug_number": "978982933", "supervisor_username": "daniel.chalwe" },
  { "name": "Guardian Mwenya",      "cug_number": "978982856", "supervisor_username": "daniel.chalwe" },
  { "name": "Harrison Mbewe",       "cug_number": "978982909", "supervisor_username": "daniel.chalwe" },

  { "name": "Abraham Mwale",        "cug_number": "978982570", "supervisor_username": "gibson.nkole" },
  { "name": "Carlos Chishala",      "cug_number": "978982176", "supervisor_username": "gibson.nkole" },
  { "name": "Davies Chinta",        "cug_number": "978982640", "supervisor_username": "gibson.nkole" },
  { "name": "Dennis Mulenga",       "cug_number": "978982873", "supervisor_username": "gibson.nkole" },
  { "name": "Faith Chuma",          "cug_number": "978982927", "supervisor_username": "gibson.nkole" },
  { "name": "Mwenda Kasinda",       "cug_number": "978982612", "supervisor_username": "gibson.nkole" },
  { "name": "Francis Chikumbi",     "cug_number": "978982465", "supervisor_username": "gibson.nkole" },
  { "name": "Natasha Banda",        "cug_number": "978982658", "supervisor_username": "gibson.nkole" },
  { "name": "Corban Mweemba",       "cug_number": "978982080", "supervisor_username": "gibson.nkole" },
  { "name": "George Mazimba",       "cug_number": "978982876", "supervisor_username": "gibson.nkole" },
  { "name": "Dalitso Zulu",         "cug_number": "978982605", "supervisor_username": "gibson.nkole" },
  { "name": "Lottie Mwritabe",      "cug_number": "978982586", "supervisor_username": "gibson.nkole" },
  { "name": "Mwiza Mfuni",          "cug_number": "978982607", "supervisor_username": "gibson.nkole" },
  { "name": "Lawrence Sikutwa",     "cug_number": "978982608", "supervisor_username": "gibson.nkole" },
  { "name": "Georgina Mwanza",      "cug_number": "978982938", "supervisor_username": "gibson.nkole" }
]
```

---

> [!IMPORTANT]
> **Duplicate CUG Check:** I noticed `978982664` appears under both **Victor Zembo** (Kasonde Mukuka) and **Joseph Nkhoma** (Lenario Malambo). MongoDB will reject the second insert because of the duplicate CUG check in the code. Please verify these two numbers from the original sheet before inserting.

> [!NOTE]
> **Also note:** `978982608` appears under both **Victor Zembo** (Mwape Chishala) and **Gibson Nkole** (Lawrence Sikutwa). Please double-check these as well.
