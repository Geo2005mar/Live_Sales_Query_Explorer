# Live Sales Query Explorer

Personal project: μια MySQL βάση δεδομένων που ενημερώνεται σε πραγματικό
χρόνο, πάνω στην οποία τρέχει ένα Streamlit web UI με φίλτρα για live
αναζήτηση δεδομένων πωλήσεων.

```
[generator.py]  --INSERT-->  [MySQL DB]  <--SELECT--  [app.py: Streamlit UI]
   (background thread,          orders            (φίλτρα + auto-refresh)
    1 νέα παραγγελία             table
    κάθε 3-5 δευτ.)
```

---

## 1. Εκφώνηση

Στόχος του project ήταν να δείξω ότι μπορώ να στήσω μια MySQL βάση, να
γράψω ερωτήματα πάνω σε δεδομένα που αλλάζουν σε πραγματικό χρόνο, και να
τα εκθέσω μέσα από ένα απλό web UI με φίλτρα.

Συγκεκριμένα, καλούμουν να υλοποιήσω:

- Ένα σχήμα βάσης δεδομένων τύπου "παραγγελίες/πωλήσεις" (`orders`).
- Ένα script που παράγει ρεαλιστικά, τυχαία δεδομένα (μέσω **Faker**) και τα
  εισάγει στη βάση **συνεχώς**, σαν να πρόκειται για πραγματική ροή
  παραγγελιών.
- Ένα web UI με **προκαθορισμένα φίλτρα** (όχι free-text→SQL) που τρέχει
  δυναμικά SQL queries με βάση τις επιλογές του χρήστη, και ανανεώνεται
  περιοδικά ώστε να φαίνονται και οι νέες εγγραφές.

**Τι κάνει όταν τρέχει:** στο background ένα script (`generator.py`)
"γεννάει" μια νέα τυχαία παραγγελία κάθε 3-5 δευτερόλεπτα και την εισάγει
στη MySQL. Παράλληλα, ένα Streamlit UI (`app.py`) δείχνει πίνακα με τις
παραγγελίες, επιτρέπει φιλτράρισμα (ημερομηνία, κατηγορία, χώρα, ποσό) και
αυτο-ανανεώνεται ώστε να βλέπεις τις νέες εγγραφές να εμφανίζονται ζωντανά,
χωρίς να κάνεις εσύ manual refresh.

---

## 2. Σχεδιαστικές επιλογές & δομή project

### Αρχιτεκτονική

Δύο εντελώς ανεξάρτητα Python scripts μιλάνε μεταξύ τους **μόνο μέσω της
βάσης δεδομένων** — δεν έχουν καμία άμεση σύνδεση/επικοινωνία μεταξύ τους.
Αυτό κρατάει το κάθε κομμάτι απλό και το προσομοιώνει ρεαλιστικά ως δύο
ξεχωριστές εφαρμογές (ένα data producer, ένα data consumer):

- **`generator.py`** — παίζει τον ρόλο του "producer". Την πρώτη φορά που
  τρέχει, γεμίζει τη βάση με 500-1000 ιστορικές εγγραφές (seed), και μετά
  μπαίνει σε ατέρμονο βρόχο που εισάγει 1 νέα τυχαία παραγγελία κάθε 3-5
  δευτερόλεπτα, προσομοιώνοντας ζωντανή ροή πωλήσεων.
- **`app.py`** — παίζει τον ρόλο του "consumer". Είναι ένα Streamlit UI που
  διαβάζει τη βάση με `SELECT` queries χτισμένα δυναμικά από τα φίλτρα του
  χρήστη, και ξανατρέχει το query περιοδικά (auto-refresh) ώστε να
  εμφανίζονται και οι εγγραφές που πρόσθεσε ο generator στο μεταξύ.

### Δομή αρχείων

```
Live_Sales_Query_Explorer/
├── app.py              Streamlit UI: φίλτρα, dynamic SQL query builder, πίνακας, μετρικές, chart
├── generator.py        Background live data generator: seed δεδομένων + loop με τυχαία inserts
├── config.py            Κοινές ρυθμίσεις: DB credentials (από .env) + σταθερές (κατηγορίες/προϊόντα, χώρες, όρια ποσού)
├── db/
│   └── init.sql         SQL schema: ορισμός του πίνακα orders (στήλες, indexes)
├── docker-compose.yml   Ορισμός του MySQL container (image, port, volume, healthcheck)
├── requirements.txt     Λίστα Python dependencies
├── .env.example         Παράδειγμα μεταβλητών σύνδεσης με τη βάση (αντιγράφεται σε .env)
└── README.md            Το παρόν αρχείο
```

Το `config.py` υπάρχει ως ξεχωριστό αρχείο ώστε οι σταθερές (π.χ. λίστα
κατηγοριών/προϊόντων, λίστα χωρών) να ορίζονται **μία φορά** και να
χρησιμοποιούνται και από τον `generator.py` (τι δεδομένα παράγει) και από
το `app.py` (τι επιλογές εμφανίζει στα dropdown φίλτρα) — έτσι τα φίλτρα
του UI ταιριάζουν πάντα ακριβώς με τα δεδομένα που υπάρχουν στη βάση.

### Σχήμα βάσης δεδομένων

Πίνακας `orders`:

| Στήλη | Τύπος | Περιγραφή |
|---|---|---|
| `order_id` | `INT AUTO_INCREMENT PK` | Μοναδικό αναγνωριστικό παραγγελίας |
| `customer_name` | `VARCHAR(255)` | Όνομα πελάτη (Faker) |
| `country` | `VARCHAR(100)` | Χώρα παραγγελίας (από προκαθορισμένη λίστα) |
| `category` | `VARCHAR(100)` | Κατηγορία προϊόντος |
| `product` | `VARCHAR(255)` | Συγκεκριμένο προϊόν εντός της κατηγορίας |
| `amount` | `DECIMAL(10,2)` | Ποσό παραγγελίας σε € |
| `order_date` | `DATETIME` | Ημερομηνία/ώρα παραγγελίας |

Υπάρχουν indexes στα `order_date`, `category`, `country` επειδή είναι
ακριβώς οι στήλες πάνω στις οποίες φιλτράρει το UI — έτσι τα `WHERE`
queries παραμένουν γρήγορα ακόμα κι όταν ο πίνακας μεγαλώνει συνεχώς.

### Dynamic query builder

Το `app.py` δεν τρέχει ένα στατικό query — χτίζει το `WHERE` clause
δυναμικά ανάλογα με το ποια φίλτρα έχει επιλέξει ο χρήστης (π.χ. αν δεν
έχει επιλεγεί καμία χώρα, δεν προστίθεται καθόλου συνθήκη για `country`).
Όλες οι τιμές περνάνε ως **parameterized query** (`%s` placeholders) και
όχι με string concatenation, ώστε να αποφεύγεται SQL injection.

---

## 3. Εργαλεία & τεχνολογίες που χρησιμοποιήθηκαν

- **MySQL 8.0** — η βάση δεδομένων. Τρέχει μέσα σε **Docker container**
  αντί για native εγκατάσταση, ώστε το project να είναι αναπαραγώγιμο σε
  οποιοδήποτε μηχάνημα με μία εντολή, χωρίς να "λερώνει" το σύστημα με
  global MySQL εγκατάσταση.
  - Ο ορισμός του container βρίσκεται στο `docker-compose.yml`: χρησιμοποιεί
    το επίσημο image `mysql:8.0`, εκθέτει το port `3306` στο localhost, και
    ορίζει ένα named **volume** (`db_data`) ώστε τα δεδομένα να επιβιώνουν
    ακόμα κι αν το container σταματήσει/επανεκκινήσει.
  - Το `db/init.sql` γίνεται mount μέσα στο container στον φάκελο
    `/docker-entrypoint-initdb.d/`, που είναι ένας ειδικός φάκελος του
    επίσημου MySQL image: οτιδήποτε `.sql` αρχείο βρεθεί εκεί εκτελείται
    **αυτόματα, μία φορά, κατά το πρώτο startup** του container (δημιουργεί
    τον πίνακα `orders`) — δεν χρειάζεται να τρέξω εγώ χειροκίνητα κάποιο
    migration script.
  - Ένα `healthcheck` στο compose file (μέσω `mysqladmin ping`) επιτρέπει να
    ξέρω πότε η βάση είναι πραγματικά έτοιμη να δεχτεί συνδέσεις, και όχι
    απλώς ότι το container ξεκίνησε.
- **Docker Compose** — χρησιμοποιείται (αντί για σκέτο `docker run`) ώστε
  όλη η ρύθμιση (image, ports, volumes, environment variables, healthcheck)
  να είναι δηλωμένη σε ένα αρχείο και να ξεκινάει/σταματάει με μία εντολή
  (`docker compose up -d` / `docker compose down`).
- **Faker (Python library)** — παράγει ρεαλιστικά ονόματα πελατών αυτόματα,
  ώστε να μη χρειάζεται να κατεβάσω/βρω κάποιο έτοιμο dataset.
- **mysql-connector-python** — επίσημος driver της Oracle για σύνδεση
  Python↔MySQL· χρησιμοποιείται και από τα δύο scripts για `INSERT`
  (generator) και `SELECT` (app) queries, πάντα με parameterized queries.
- **Streamlit** — framework για το web UI. Επιλέχθηκε γιατί επιτρέπει να
  φτιάξω interactive UI (dropdowns, sliders, πίνακες, κουμπιά) γράφοντας
  μόνο Python, χωρίς HTML/CSS/JS.
- **streamlit-autorefresh** — μικρό πρόσθετο πακέτο που κάνει το Streamlit
  script να ξανατρέχει αυτόματα κάθε Ν δευτερόλεπτα (ρυθμιζόμενο από το
  UI), ώστε το query στη βάση να επαναλαμβάνεται μόνο του και να
  εμφανίζονται οι νέες εγγραφές χωρίς χειροκίνητο reload της σελίδας.
- **pandas** — μετατρέπει τα αποτελέσματα του SQL query σε DataFrame, το
  οποίο το Streamlit ξέρει να εμφανίζει απευθείας ως interactive πίνακα
  (`st.dataframe`) και να το χρησιμοποιεί για το bar chart.
- **python-dotenv** — φορτώνει τα credentials της βάσης (host, port, user,
  password, database name) από το αρχείο `.env`, ώστε να μην είναι
  hardcoded μέσα στον κώδικα.

---

## 4. Οδηγός εκτέλεσης (για να το τρέξεις τοπικά)

### Προαπαιτούμενα

- Docker + Docker Compose
- Python 3.10+

### Βήματα

**α) Κλωνοποίησε/κατέβασε τον φάκελο του project και μπες μέσα**

```bash
cd Live_Sales_Query_Explorer
```

**β) Ξεκίνα τη MySQL**

```bash
docker compose up -d
```

Αυτό κατεβάζει (αν δεν υπάρχει ήδη τοπικά) το image `mysql:8.0` και στήνει
το container `sales_mysql` στο `localhost:3306`, με database `sales_db` και
τον πίνακα `orders` έτοιμο (μέσω `db/init.sql`). Μπορείς να δεις αν είναι
έτοιμη με `docker compose ps` (θέλεις status `healthy`).

Οι μεταβλητές σύνδεσης βρίσκονται στο `.env` (δημιουργείται αντιγράφοντας
το `.env.example`):

```bash
cp .env.example .env
```

**γ) Δημιούργησε virtual environment & εγκατέστησε τα Python dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**δ) Ξεκίνα τον generator (σε ένα terminal)**

```bash
source .venv/bin/activate
python generator.py
```

Την πρώτη φορά θα κάνει seed 500-1000 ρεαλιστικές παραγγελίες με
ημερομηνίες τις τελευταίες 60 ημέρες. Μετά μπαίνει σε βρόχο και εισάγει μια
νέα τυχαία παραγγελία κάθε 3-5 δευτερόλεπτα. **Άφησέ το να τρέχει.**

**ε) Ξεκίνα το Streamlit UI (σε δεύτερο terminal)**

```bash
cd Live_Sales_Query_Explorer
source .venv/bin/activate
streamlit run app.py
```

Άνοιξε το [http://localhost:8501](http://localhost:8501) στον browser. Από
το sidebar μπορείς να φιλτράρεις με:

- Εύρος ημερομηνιών
- Κατηγορία προϊόντος
- Χώρα
- Ελάχιστο/μέγιστο ποσό
- Κουμπί "Αναζήτηση"
- Auto-refresh (ενεργό by default, ρυθμιζόμενο interval) ώστε να φαίνονται
  και οι νέες εγγραφές που προσθέτει ο generator χωρίς manual reload

Ο πίνακας αποτελεσμάτων δείχνει "Total rows", "Total revenue" και "Avg
order value" για το τρέχον φίλτρο, μαζί με ένα bar chart εσόδων ανά
κατηγορία.

### Τερματισμός

```bash
# Ctrl+C στα δύο terminals (generator, streamlit)

docker compose down        # σταματά τη MySQL (τα δεδομένα μένουν στο volume db_data)
docker compose down -v     # σταματά τη MySQL ΚΑΙ διαγράφει τα δεδομένα
```

