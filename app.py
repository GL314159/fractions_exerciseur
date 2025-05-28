import streamlit as st
import random
from fractions import Fraction
import pandas as pd

NB_QUESTIONS = 8





# --- Niveaux disponibles ---
NIVEAUX = {
    "Additions seulement": ["+"],
    "Simplification uniquement": ["="],
    "Niveau difficile": ["+", "-", "*", ":"]
}

previous_level = st.session_state.get("niveau_selectionne", None)
#niveau = st.selectbox("🎯 Choisis un niveau", list(NIVEAUX.keys()))

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        margin-top: -35px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
col1, col2 = st.columns([1, 2.5])  # [texte, selectbox]
with col2:
    niveau = st.selectbox("", list(NIVEAUX.keys()))
with col1:
    st.markdown("🎯 $\;$ **Choisissez un niveau**")
st.session_state.niveau_selectionne = niveau







# --- Générer une question selon le niveau ---
def generer_question():
    a, b = random.randint(1, 9), random.randint(1, 9)
    if niveau == "Simplification uniquement":
        k = random.randint(2, 5)
        a *= k
        b *= k
        return (a, b, "=", 0, 0)
    else:
        c, d = random.randint(1, 9), random.randint(1, 9)
        op = random.choice(NIVEAUX[niveau])
        return (a, b, op, c, d)

def calculer_resultat(a, b, op, c, d):
    f1, f2 = Fraction(a, b), Fraction(c, d) if d != 0 else Fraction(1, 1)
    if op == "+": return f1 + f2
    elif op == "-": return f1 - f2
    elif op == "*": return f1 * f2
    elif op == ":": return f1 / f2
    elif op == "=": return Fraction(a, b)

def latex_fraction(frac):
    return f"\\dfrac{{\\mathsf{{{frac.numerator}}}}}{{\\mathsf{{{frac.denominator}}}}}"

def latex_frac(a, b):
    return f"\\dfrac{{\\mathsf{{{a}}}}}{{\\mathsf{{{b}}}}}"

def explication_operation(a, b, op, c, d):
    f1, f2 = Fraction(a, b), Fraction(c, d) if d != 0 else Fraction(1, 1)

    if op == "=":
        f = Fraction(a, b)
        st.markdown("Tu dois **simplifier** la fraction :")
        st.latex(rf"{latex_frac(a, b)} = {latex_fraction(f)}")
        return

    if op in ["+", "-"]:
        operation = "addition" if op == "+" else "soustraction"
        st.markdown(f"Pour faire une **{operation}**, il faut mettre les deux fractions au même dénominateur.")
        st.markdown(rf"On a : $\displaystyle {latex_frac(a,b)}$ et $\displaystyle {latex_frac(c, d)}$")
        result = f1 + f2 if op == "+" else f1 - f2
        st.markdown(rf"On calcule : $\displaystyle {latex_fraction(f1)} \; {op} \; {latex_fraction(f2)} = {latex_fraction(result)}$")
    elif op == "*":
        result = Fraction(a * c, b * d)
        st.markdown("Pour **multiplier** deux fractions, on multiplie les numérateurs et les dénominateurs :")
        st.markdown(rf"$\displaystyle {latex_frac(a,b)} \times {latex_frac(c,d)} = {latex_fraction(result)}$")
    elif op == ":":
        result = Fraction(a * d, b * c)
        st.markdown("Diviser par une fraction, c’est multiplier par son inverse :")
        st.markdown(rf"$\displaystyle {latex_frac(a,b)} \div {latex_frac(c, d)} = \dfrac{{{a}}}{{{b}}} \times \dfrac{{{d}}}{{{c}}} = {latex_fraction(result)}$")

# --- Initialisation ---
if "question" not in st.session_state:
    st.session_state.question = generer_question()
if "question_num" not in st.session_state:
    st.session_state.question_num = 1
if "score" not in st.session_state:
    st.session_state.score = 0
if "historique" not in st.session_state:
    st.session_state.historique = []
if "correction_validee" not in st.session_state:
    st.session_state.correction_validee = False


if previous_level and niveau != previous_level:
    st.session_state.question_num = 1
    st.session_state.score = 0
    st.session_state.historique = []
    st.session_state.correction_validee = False
    st.session_state.question = generer_question()
    st.rerun()


# --- Fin de quiz ---
if st.session_state.question_num > NB_QUESTIONS:
    st.title("🎉 Exercice terminé !")
    st.success(f"🏁 Score final : **{st.session_state.score} / {NB_QUESTIONS}**")
    df = pd.DataFrame(st.session_state.historique)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger les résultats", csv, "resultats_fractions.csv", "text/csv")
    st.stop()

# --- Affichage de la question ---
a, b, op, c, d = st.session_state.question
st.markdown("#### Calculons avec des fractions !")  # un peu plus grand

progress = (st.session_state.question_num - 1) / NB_QUESTIONS * 100

st.markdown(
    f"""
    <div style='display: flex; align-items: center; gap: 1em;'>
        <div style='font-size: 1rem; white-space: nowrap;'>
            📘 Question {st.session_state.question_num} / {NB_QUESTIONS}
        </div>
        <div style='flex-grow: 1; background: #eee; height: 10px; border-radius: 5px;'>
            <div style='width: {progress}%; background: #2b8fe5; height: 100%; border-radius: 5px;'></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
st.info(f"Score actuel : {st.session_state.score} / {st.session_state.question_num - 1}")

op_map = {"+": "+", "-": "-", "*": r"\times", ":": r"\div", "=": "="}
if op == "=":
    expr = rf"\displaystyle {latex_frac(a,b)}"
    st.markdown("Simplifie la fraction suivante :")
else:
    expr = rf"\displaystyle {latex_frac(a,b)} \; {op_map[op]} \; {latex_frac(c, d)}"

st.latex(expr)

# --- Champ de réponse ---
input_key = f"reponse_input_{st.session_state.question_num}"
already_corrected = st.session_state.correction_validee

with st.form("form_reponse"):
    reponse = st.text_input("✍️ Votre réponse (format a/b)", key=input_key, disabled=already_corrected)
    submit = st.form_submit_button("✅ Vérifier", use_container_width=True)

if submit and not already_corrected:
    try:
        if "/" in reponse:
            num, den = map(int, reponse.strip().split("/"))
            rep_utilisateur = Fraction(num, den)
        else:
            rep_utilisateur = Fraction(int(reponse.strip()), 1)

        resultat = calculer_resultat(a, b, op, c, d)
        est_correct = rep_utilisateur == resultat

        if est_correct:
            st.success("✅ Bonne réponse ! Bravo !")
            st.session_state.score += 1
        else:
            st.error(f"❌ Mauvaise réponse. $\quad$ **La bonne réponse est** $\quad\displaystyle {latex_fraction(resultat)}$")
            #st.markdown(rf"**La bonne réponse était :** $\dfrac{{{resultat.numerator}}}{{{resultat.denominator}}}$")
            with st.expander("💡 Explication détaillée", expanded=False):
                explication_operation(a, b, op, c, d)

        st.session_state.historique.append({
            "Niveau": niveau,
            "Question": f"{a}/{b} {op} {c}/{d}" if op != "=" else f"{a}/{b}",
            "Réponse élève": reponse,
            "Bonne réponse": str(resultat),
            "Correct": "✅" if est_correct else "❌"
        })
        st.session_state.correction_validee = True

    except:
        st.warning("❗ Format invalide. Exemple : `3/4` ou `2`.")

# --- Suivant ---
if st.button("➡️ Question suivante", use_container_width=True):
    st.session_state.question_num += 1
    st.session_state.question = generer_question()
    st.session_state.correction_validee = False
    st.rerun()






def get_visite_count():
    try:
        with open("visites.txt", "r") as f:
            count = int(f.read())
    except:
        count = 0
    return count

def increment_visite_count():
    count = get_visite_count() + 1
    with open("visites.txt", "w") as f:
        f.write(str(count))
    return count

if "visite_enregistree" not in st.session_state:
    total = increment_visite_count()
    st.session_state.visite_enregistree = True
else:
    total = get_visite_count()


st.markdown(
    f"<div style='text-align: right; font-size: 0.2em; color: grey; margin-top: 4em;'>"
    f"Nombre de visites : {total}"
    f"</div>",
    unsafe_allow_html=True
)
