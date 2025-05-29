import streamlit as st
import random
from fractions import Fraction
import pandas as pd
import math



st.markdown(
    "<div style='text-align: center; font-size: 24px; font-weight: bold; color: orange;'>"
    "Calculons avec des fractions !"
    "</div>",
    unsafe_allow_html=True
)




# --- Niveaux disponibles ---
NIVEAUX = {
    "1 — Simplification uniquement": ["="],
    "2 — Addition seulement": ["+"],
    "3 — Mélange": ["+", "-", "*", ":"]
}

previous_level = st.session_state.get("niveau_selectionne", None)

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
    st.markdown("**Choisissez un niveau**")

st.session_state.niveau_selectionne = niveau









# Définir le nombre de questions selon le niveau
if niveau == "3 — Mélange":
    NB_QUESTIONS = 10
else:
    NB_QUESTIONS = 8

if niveau == "3 — Mélange" and "operations_melange" not in st.session_state:
    ops = ["*", "*", ":", ":"] + random.choices(["+", "-"], k = NB_QUESTIONS - 4 + 1)   #Il y aura 2 multipications, 2 divisions et le reste : + ou -
    random.shuffle(ops)
    st.session_state.operations_melange = ops




# --- Générer une question selon le niveau ---
if "deja_eu" not in st.session_state:
    st.session_state.deja_eu = []

def generer_question():
    a, b = 2, 2
    while math.gcd(a, b) > 1 or (a, b) in st.session_state.deja_eu:
        a = random.randint(1, 10)
        b = random.randint(1, 10)
    if niveau == "1 — Simplification uniquement":
        k = random.randint(2, 5)
        a *= k
        b *= k
        st.session_state.deja_eu.append((a, b))
        return (a, b, "=", 0, 0)
    else:
        a, b, c, d = 2, 2, 2, 2
        while math.gcd(c, d) > 1 or math.gcd(a, b) > 1   or   (a, b) in st.session_state.deja_eu   or  b*d==1  or (a,b)==(c,d):
            a = random.randint(1, 6) # pas besoin de numérateurs très grands
            b = random.randint(1, 10)
            c = random.randint(1, 6) # pas besoin de numérateurs très grands
            d = random.randint(1, 10)
        st.session_state.deja_eu.append((a, b)) # NB : il y a 23 couples d'entiers (a,b) entre 1 et 6 compris tels que gcd(a,b)==1 donc on peut avoir maximum 26 questions
        if niveau == "3 — Mélange":
            op = st.session_state.operations_melange[st.session_state.question_num - 1]
        else:
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
    if frac.denominator != 1:
        return f"\\dfrac{{\\mathsf{{{frac.numerator}}}}}{{\\mathsf{{{frac.denominator}}}}}"
    return f"\\mathsf{{{frac.numerator}}}"

def latex_frac(a, b):
    if b == 1:
        return f"\\mathsf{{{a}}}"
    else:
        return f"\\dfrac{{\\mathsf{{{a}}}}}{{\\mathsf{{{b}}}}}"

def explication_operation(a, b, op, c, d, num, den): #num, den = ce qu'a rentré l'utilisateur
    f1, f2 = Fraction(a, b), Fraction(c, d) if d != 0 else Fraction(1, 1)

    if op == "=":
        f = Fraction(a, b)
        a1 = a // f.numerator
        b1 = b // f.denominator
        assert(a1 == b1)
        st.markdown("Pour **simplifier** une fraction, on factorise le numérateur et le dénominateur :")
        st.latex(rf"{latex_frac(a, b)} \;=\; \dfrac{{\mathsf{{{a1}}} \cdot \mathsf{{{f.numerator}}}}}{{\mathsf{{{b1}}} \cdot \mathsf{{{f.denominator}}}}}   \;=\;   {latex_fraction(f)}")
        return

    if op in ["+", "-"]:
        result = f1 + f2 if op == "+" else f1 - f2
        if Fraction(num, den) == result and den != result.denominator:
            st.markdown(f"C'est presque juste ! Vous avez uniquement oublié de simplifier la fraction.")
        else:
            operation = "addition" if op == "+" else "soustraction"
            st.markdown(f"Pour faire une **{operation}**, il faut mettre les deux fractions au même dénominateur.")
            M = math.lcm(b, d)
            st.markdown(f"Ici, le plus petit dénominateur commun est {M}.")
            #### quid si les fractions ne sont pas simplifiées au départ ? ***
            st.markdown(rf"On amplifie chaque fraction : $\quad\displaystyle {latex_frac(a,b)} = {latex_frac(a*math.lcm(b, d)//b, M)}\quad$ et $\quad\displaystyle {latex_frac(c, d)}= {latex_frac(c*math.lcm(b, d)//d, M)}\quad$")
            st.markdown(rf"On déduit donc que $\quad\displaystyle {latex_fraction(f1)} \; {op} \; {latex_fraction(f2)} \;=\; {latex_frac(a*math.lcm(b, d)//b, M)} + {latex_frac(c*math.lcm(b, d)//d, M)} \;=\; {latex_frac(a*math.lcm(b, d)//b  +  c*math.lcm(b, d)//d, M)}$")
            if result.denominator != M:
                st.markdown(rf"Finalement, on simplifie la fraction obtenue : $\quad\displaystyle {latex_frac(a*math.lcm(b, d)//b  +  c*math.lcm(b, d)//d, M)} \;=\; {latex_fraction(result)}$")

    elif op == "*":
        result = Fraction(a * c, b * d)
        if Fraction(num, den) == result and den != result.denominator:
            st.markdown(f"C'est presque juste ! Vous avez uniquement oublié de simplifier la fraction.")
        else:
            st.markdown("Pour **multiplier** deux fractions, on multiplie les numérateurs et les dénominateurs :")
            st.markdown(rf"$\displaystyle {latex_frac(a,b)} \cdot {latex_frac(c,d)}  \;=\;  {latex_fraction(result)}$")
    elif op == ":":
        result = Fraction(a * d, b * c)
        if Fraction(num, den) == result and den != result.denominator:
            st.markdown(f"C'est presque juste ! Vous avez uniquement oublié de simplifier la fraction.")
        else:
            st.markdown("Diviser par une fraction, c’est multiplier par son inverse :")
            st.markdown(rf"$\displaystyle {latex_frac(a,b)} \div {latex_frac(c, d)}  \;=\;  \dfrac{{{a}}}{{{b}}} \cdot \dfrac{{{d}}}{{{c}}} = {latex_fraction(result)}$")





# --- Initialisation ---
if "question" not in st.session_state:
    st.session_state.question = generer_question()
if "question_num" not in st.session_state:
    st.session_state.question_num = 1
if "nb_questions" not in st.session_state:
    st.session_state.nb_questions = NB_QUESTIONS
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
    st.session_state.deja_eu = []
    st.session_state.nb_questions = NB_QUESTIONS  # ← à ajouter ici
    st.session_state.question = generer_question()
    st.rerun()




# --- Fin de quiz ---
if st.session_state.question_num > st.session_state.nb_questions:
    st.markdown("#### 🎉 Exercice terminé !")
    st.success(f"🏁 Score final : **{st.session_state.score} / {st.session_state.nb_questions}**")
    df = pd.DataFrame(st.session_state.historique)
    st.dataframe(df)
    col1, col2 = st.columns([3, 1])

    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Télécharger les résultats", csv, "resultats_fractions.csv", "text/csv")

    with col2:
        if st.button("🔄 Recommencer"):
            # Réinitialiser tous les éléments de session
            st.session_state.question_num = 1
            st.session_state.score = 0
            st.session_state.historique = []
            st.session_state.correction_validee = False
            st.session_state.deja_eu = []
            st.session_state.question = generer_question()
            st.rerun()

    st.stop()










# --- Affichage de la question ---
a, b, op, c, d = st.session_state.question

progress = (st.session_state.question_num - 1) / st.session_state.nb_questions * 100

st.markdown(
    f"""
    <div style='display: flex; align-items: center; gap: 1em;'>
        <div style='font-size: 1rem; white-space: nowrap;'>
            Question {st.session_state.question_num} sur {st.session_state.nb_questions}
        </div>
        <div style='flex-grow: 1; background: #eee; height: 10px; border-radius: 5px;'>
            <div style='width: {progress}%; background: #2b8fe5; height: 100%; border-radius: 5px;'></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
st.info(f"Score actuel : {st.session_state.score} sur {st.session_state.question_num - 1}")

op_map = {"+": "+", "-": "-", "*": r"\cdot", ":": r"\div", "=": "="}
if op == "=":
    st.markdown(f"Simplifier la fraction suivante : $\qquad\\displaystyle {latex_frac(a, b)}$")

else:
    st.markdown(f"Écrire sous forme de fraction irréductible : $\qquad\\displaystyle {latex_frac(a,b)} \; {op_map[op]} \; {latex_frac(c, d)}$")

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
            num = rep_utilisateur.numerator
            den = 1

        resultat = calculer_resultat(a, b, op, c, d)
        est_correct = (rep_utilisateur == resultat and math.gcd(num,den)==1)

        if est_correct:
            st.success("✅ Réponse correcte ! Bravo !")
            st.session_state.score += 1
        else:
            st.error(f"❌ Réponse incorrecte.  \n**La réponse correcte est** $\quad\\displaystyle {latex_fraction(resultat)}$")
            #  deux espaces avant le \n !!!
            with st.expander("💡 Explication détaillée", expanded=False):
                explication_operation(a, b, op, c, d, num, den)

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
    G = generer_question()
    st.session_state.question = G
    st.session_state.correction_validee = False
    st.rerun()





# --- Nombre de visites ---
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
    rf"Développé par G. Leterrier (Gymnase de Bussigny, 2025)   <span style='display:inline-block; width:20px;'></span>    Nombre de visites : {total}"
    f"</div>",
    unsafe_allow_html=True
)








