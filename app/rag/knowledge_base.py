"""
A small, original, general-education medical knowledge base for RAG demo
purposes. Written from scratch in plain language — NOT copied from any
external source. This is NOT a substitute for a real curated medical
knowledge base (WHO/CDC guidelines etc.) in a real deployment; see README.
"""

DOCUMENTS = [
    {
        "id": "flu_overview",
        "topic": "Influenza",
        "text": (
            "Influenza (flu) is a contagious respiratory illness caused by influenza "
            "viruses. Common symptoms include fever, cough, sore throat, body aches, "
            "headache, and fatigue. Most people recover within one to two weeks. "
            "Supportive care includes rest, staying hydrated, and using fever-reducing "
            "medication such as paracetamol as needed. Antiviral medication may be "
            "considered by a doctor if started early in high-risk patients. Anyone "
            "with difficulty breathing, persistent chest pain, or symptoms lasting "
            "more than a week without improvement should seek medical attention."
        ),
    },
    {
        "id": "common_cold_overview",
        "topic": "Common Cold",
        "text": (
            "The common cold is a mild viral infection of the nose and throat. "
            "Typical symptoms are a runny or blocked nose, sore throat, mild cough, "
            "and general tiredness, usually without high fever. It typically resolves "
            "on its own within seven to ten days. Rest, fluids, and over-the-counter "
            "cold remedies can ease symptoms. A doctor visit is recommended if "
            "symptoms worsen after a week or if breathing becomes difficult."
        ),
    },
    {
        "id": "covid_overview",
        "topic": "COVID-19",
        "text": (
            "COVID-19 is a respiratory illness caused by the SARS-CoV-2 virus. "
            "Symptoms range from mild (fever, cough, fatigue, headache) to severe "
            "(shortness of breath, chest pain, confusion). People with mild symptoms "
            "can typically rest at home, isolate to avoid spreading the virus, and "
            "monitor oxygen levels if possible. Immediate medical attention is "
            "advised for shortness of breath, persistent chest pain, or bluish "
            "lips or face."
        ),
    },
    {
        "id": "migraine_overview",
        "topic": "Migraine",
        "text": (
            "A migraine is a neurological condition causing intense, often "
            "one-sided headaches, frequently accompanied by nausea, dizziness, and "
            "sensitivity to light or sound. Triggers can include stress, certain "
            "foods, and lack of sleep. Resting in a dark, quiet room and "
            "over-the-counter pain relief can help mild episodes. Frequent or "
            "severe migraines should be evaluated by a doctor for preventive "
            "treatment options."
        ),
    },
    {
        "id": "food_poisoning_overview",
        "topic": "Food Poisoning",
        "text": (
            "Food poisoning results from eating contaminated food and typically "
            "causes nausea, vomiting, diarrhea, and stomach cramps within hours to "
            "a couple of days of eating the affected food. Most cases resolve within "
            "a few days with rest and rehydration using water or oral rehydration "
            "solutions. Medical care should be sought for signs of dehydration, "
            "blood in stool, high fever, or symptoms lasting more than a few days."
        ),
    },
    {
        "id": "gastroenteritis_overview",
        "topic": "Gastroenteritis",
        "text": (
            "Gastroenteritis is inflammation of the stomach and intestines, often "
            "caused by a viral or bacterial infection, leading to diarrhea, "
            "vomiting, nausea, and sometimes fever. Staying hydrated is the most "
            "important part of home care, since fluid loss is the main risk. "
            "Bland foods can be reintroduced gradually as symptoms improve. Seek "
            "care if there are signs of dehydration, high fever, or symptoms "
            "persisting beyond a few days."
        ),
    },
    {
        "id": "dengue_overview",
        "topic": "Dengue",
        "text": (
            "Dengue is a mosquito-borne viral infection causing high fever, severe "
            "joint and muscle pain, headache, and sometimes a skin rash. Most cases "
            "are managed with rest, fluids, and paracetamol for fever and pain — "
            "aspirin and ibuprofen should be avoided due to bleeding risk. Warning "
            "signs requiring urgent medical care include severe abdominal pain, "
            "persistent vomiting, bleeding, or difficulty breathing."
        ),
    },
    {
        "id": "bronchitis_overview",
        "topic": "Bronchitis",
        "text": (
            "Bronchitis is inflammation of the airways leading to the lungs, "
            "usually following a cold or flu, and causes a persistent cough often "
            "with mucus, chest discomfort, and mild shortness of breath. Rest, "
            "fluids, and avoiding smoke exposure typically help. A doctor should "
            "be consulted if cough lasts more than three weeks, if there is high "
            "fever, or if breathing difficulty worsens."
        ),
    },
    {
        "id": "allergic_rhinitis_overview",
        "topic": "Allergic Rhinitis",
        "text": (
            "Allergic rhinitis is an allergic response to airborne particles like "
            "pollen or dust, causing a runny or blocked nose, sneezing, itchy "
            "throat, and sometimes skin irritation. Avoiding known triggers and "
            "using antihistamines can help manage symptoms. A doctor visit is "
            "worthwhile if symptoms are frequent or significantly affect daily "
            "life, since long-term management options are available."
        ),
    },
    {
        "id": "viral_fever_overview",
        "topic": "Viral Fever",
        "text": (
            "Viral fever refers to a fever caused by a viral infection, often "
            "accompanied by body aches, headache, and fatigue, without a clearly "
            "identified specific virus. Most viral fevers resolve within three to "
            "five days with rest, hydration, and paracetamol for fever and "
            "discomfort. Medical evaluation is recommended if fever persists "
            "beyond five days or exceeds very high temperatures."
        ),
    },
    {
        "id": "when_to_seek_emergency_care",
        "topic": "Emergency Warning Signs",
        "text": (
            "Certain symptoms always warrant immediate emergency medical "
            "attention rather than home care or general guidance: severe chest "
            "pain, significant difficulty breathing, sudden confusion or loss of "
            "consciousness, uncontrolled bleeding, signs of stroke such as facial "
            "drooping or slurred speech, and seizures. Anyone experiencing these "
            "symptoms should seek emergency care immediately rather than waiting "
            "to see if they improve."
        ),
    },
]
