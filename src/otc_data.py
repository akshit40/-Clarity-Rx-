"""
This file contains the list of allowed Over-The-Counter (OTC) medicines.
Format:
{
    "medicine_name": "Text for similarity search",
    "metadata": {"type": "Category"}
}
"""

OTC_LIST_DATA = [
    {"medicine_name": "Paracetamol (Dolo 650, Crocin)", "metadata": {"type": "Pain Relief Tablets"}},
    {"medicine_name": "Ibuprofen (Ibuprol, Brufen)", "metadata": {"type": "Pain Relief Tablets"}},
    {"medicine_name": "Diclofenac (Dicamol SR)", "metadata": {"type": "Pain Relief Tablets"}},
    {"medicine_name": "Aspirin (325mg)", "metadata": {"type": "Pain Relief Tablets"}},
    {"medicine_name": "Naproxen", "metadata": {"type": "Pain Relief Tablets"}},
    
    {"medicine_name": "Ranitidine (Rantac, Aciloc)", "metadata": {"type": "Antacid & Digestive Tablets"}},
    {"medicine_name": "Gelusil", "metadata": {"type": "Antacid & Digestive Tablets"}},
    {"medicine_name": "Digene", "metadata": {"type": "Antacid & Digestive Tablets"}},
    {"medicine_name": "Famotidine (Pepcid)", "metadata": {"type": "Antacid & Digestive Tablets"}},
    {"medicine_name": "Calcium Carbonate (Tums)", "metadata": {"type": "Antacid & Digestive Tablets"}},
    {"medicine_name": "Eno (effervescent tablets)", "metadata": {"type": "Antacid & Digestive Tablets"}},
    {"medicine_name": "Hajmola", "metadata": {"type": "Antacid & Digestive Tablets"}},
    
    {"medicine_name": "Cetirizine (10mg)", "metadata": {"type": "Cold, Cough & Allergy Tablets"}},
    {"medicine_name": "Chlorpheniramine (4mg)", "metadata": {"type": "Cold, Cough & Allergy Tablets"}},
    {"medicine_name": "Loratadine (10mg)", "metadata": {"type": "Cold, Cough & Allergy Tablets"}},
    {"medicine_name": "Fexofenadine (180mg)", "metadata": {"type": "Cold, Cough & Allergy Tablets"}},
    {"medicine_name": "Strepsils (lozenges/tablets)", "metadata": {"type": "Cold, Cough & Allergy Tablets"}},
    {"medicine_name": "Halls (lozenges)", "metadata": {"type": "Cold, Cough & Allergy Tablets"}},
    
    {"medicine_name": "Bisacodyl (Dulcolax, 5mg)", "metadata": {"type": "Laxatives & Constipation Relief"}},
    {"medicine_name": "Senna Tabs", "metadata": {"type": "Laxatives & Constipation Relief"}},
    {"medicine_name": "Docusate Sodium (100mg)", "metadata": {"type": "Laxatives & Constipation Relief"}},
    
    {"medicine_name": "Vitamin C", "metadata": {"type": "Vitamins & Supplements"}},
    {"medicine_name": "B-Complex", "metadata": {"type": "Vitamins & Supplements"}},
    {"medicine_name": "Iron tablets", "metadata": {"type": "Vitamins & Supplements"}},
    {"medicine_name": "ORS tablets", "metadata": {"type": "Vitamins & Supplements"}},
    {"medicine_name": "Lactaid", "metadata": {"type": "Vitamins & Supplements"}},
    {"medicine_name": "Centrum, Supradyn", "metadata": {"type": "Multivitamin Tablets"}},
    {"medicine_name": "Shelcal 500", "metadata": {"type": "Calcium Supplements"}},
    {"medicine_name": "Zinconia 50mg", "metadata": {"type": "Zinc Tablets"}},
    
    {"medicine_name": "Fluconazole (150mg, e.g., Forcan)", "metadata": {"type": "Antifungal Tablets"}},
    {"medicine_name": "Itraconazole (e.g., Sporanox)", "metadata": {"type": "Antifungal Tablets"}},
    
    {"medicine_name": "N-Acetylcarnosine drops (Can-C equivalent)", "metadata": {"type": "Eye Care Tablets/Drops (Oral)"}},
    {"medicine_name": "Otrivin ear drops (decongestant)", "metadata": {"type": "Ear Care Tablets"}},
    
    {"medicine_name": "Isotretinoin (low-dose, e.g., Sotret)", "metadata": {"type": "Acne Treatment Tablets"}},
    
    {"medicine_name": "Loperamide (2mg, e.g., Imodium)", "metadata": {"type": "Anti-Diarrheal Tablets"}},
    {"medicine_name": "Racecadotril (e.g., Redytron)", "metadata": {"type": "Anti-Diarrheal Tablets"}},
    {"medicine_name": "Electral (ORS variant)", "metadata": {"type": "Electrolyte Tablets"}},
    
    {"medicine_name": "Meclizine (25mg)", "metadata": {"type": "Motion Sickness Tablets"}},
    {"medicine_name": "Melatonin (3-5mg)", "metadata": {"type": "Sleep Aid Tablets"}},
    
    {"medicine_name": "Albendazole (400mg)", "metadata": {"type": "Anthelmintic Tablets"}},
    {"medicine_name": "Daflon 500", "metadata": {"type": "Hemorrhoid Tablets"}}
]
