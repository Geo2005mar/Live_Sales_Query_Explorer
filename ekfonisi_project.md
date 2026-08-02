# Εκφώνηση Project: Live Sales Query Explorer (MySQL + Streamlit)

**Στόχος:** Εφαρμογή που δείχνει ότι μπορείς να στήσεις μια MySQL βάση, να κάνεις ερωτήματα πάνω σε δεδομένα που αλλάζουν σε πραγματικό χρόνο, και να τα εκθέτεις μέσα από ένα απλό web UI με φίλτρα.

---

## 1. Dataset — δεν χρειάζεται να κατεβάσεις κάτι μεγάλο

Αφού η βάση θα ανανεώνεται live, καλύτερα να **μη** βασιστείς σε στατικό dataset. Πρόταση:

- Φτιάξε ένα σχήμα τύπου "παραγγελίες/πωλήσεις" (orders):
  `order_id, customer_name, country, category, product, amount, order_date`
- Seed (αρχικά δεδομένα) με τη βιβλιοθήκη **Faker** (Python) — παράγεις 500-1000 ρεαλιστικές εγγραφές αυτόματα, χωρίς download.

---

## 2. Αρχιτεκτονική

```
[generator.py]  --INSERT-->  [MySQL DB]  <--SELECT--  [app.py: Streamlit UI]
   (τρέχει σε
    background,
    προσθέτει 1 νέα
    εγγραφή κάθε
    λίγα δευτερόλεπτα)
```

- **generator.py**: ξεχωριστό script/thread που κάθε 3-5 δευτ. κάνει `INSERT` μια νέα τυχαία παραγγελία (μέσω Faker) στη MySQL. Αυτό προσομοιώνει τη "συνεχή ανανέωση".
- **app.py**: Streamlit app που τρέχει `SELECT` queries με βάση τα φίλτρα του χρήστη, και ανανεώνεται περιοδικά (`st.autorefresh` ή refresh button) ώστε να φαίνονται και οι νέες εγγραφές.

---

## 3. UI — προκαθορισμένα φίλτρα (χωρίς free-text→SQL)

- Εύρος ημερομηνιών
- Κατηγορία προϊόντος (dropdown)
- Χώρα (dropdown)
- Ελάχιστο/μέγιστο ποσό (slider)
- Κουμπί "Αναζήτηση" → τρέχει το SQL query με WHERE clauses ανάλογα με τα επιλεγμένα φίλτρα
- Πίνακας αποτελεσμάτων + ένδειξη "Total rows: X" που ανανεώνεται

---

## 4. Βήματα υλοποίησης

1. Στήσε MySQL (τοπικά ή Docker), δημιούργησε database + table
2. Γράψε `generator.py` (Faker + `mysql-connector-python`, loop με `time.sleep`)
3. Γράψε `app.py` (Streamlit, `mysql-connector-python`, δυναμικό SQL query builder με βάση τα φίλτρα)
4. Πρόσθεσε auto-refresh στο UI

---

## 5. Παραδοτέα

- Κώδικας (`generator.py`, `app.py`, `requirements.txt`)
- README με οδηγίες εκτέλεσης
- 1-2 screenshots/GIF του UI σε δράση
