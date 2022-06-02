# Copyright 2021 NextERP Romania SRL
# License OPL-1.0 or later
# (https://www.odoo.com/documentation/user/14.0/legal/licenses/licenses.html#).


# Import de date se realizeaza pe un model, model parinte. Pe langa acest model in fisier de import mai pot sa fie date ale  altor modelor
# relationate cu acesta ( module relationate atat in dreapta cat si in stanga ). Modele (atat parinte cat si cele relationate) pot sa contina  campuri
# care sunt cheii ale unor altor #modele( il vom numi idmodel) cu care sunt  relationate. Idmodel nu se foloseste atunci  cand trebuie sa sa fie create
# si populate cu multe campuri. Definirea modelelor #care vor fi importate , a relatilor dintrea ele , a campurilor pe care fiecare model in contine se face
# cu ajutorul dictionarelor header.
# Dictionarul cu campurile care este folosit la import poate sa fie generic  notat la final _g sau cu _d in cazul in care  contine valorile default.
# Dictionarul generic are ca si  chei campurile modelui care va fi creat.
#     field_model:(translate_name,model,relationar_model,list((camp_relationat,XXX),...)
# Valoarea unei cheie poate sa fie 0 caz in care campul va fi ignorat sau o pereche ( tulupe).
# Perechea  este de format din 4 cifre (Nume,model,model_relationat, chei de cautare)
# Nume - este numele campului asa cum aparare in fiserul de import, este cat mai sugestiv pentru client
# model este numele modelul de care apartine campul, pot sa fie mai multe modele care se importa dintr-un fisier. Primul model este modelul parinte
# modele care sunt intr-un rand contin valori astfel incat ele sa poate fi create si sunt relatinate intre ele.
# modelul relationar- in acest caz camupul este o cheie externa  modelelul cu care se leaga
# cheia de cautare - este cheia care cauta ingregistrarea in modelul relational, in cazul in care nu il gaseste creaza o inregistrare
# este o lista de tulupuri sunt trei tipuri de chei un tulup (nume_camp_relationat, None) - se cauta valoare din coloana respectiva si se relationeza cu
# modelul campului , (nume_camp_relatinar, nume_camp_din modelul) valoarea este luata din colana cu nume_camp_model si este cauta modelul relationat   unui  camp
# (nume_camp_relationar, valoare_default ) valoarea default se cauta in campul relationat daca nu exista se creeaz


header_bom_line = {
    "bom_id": "ID_bom",
    "code": "Code_bom",
    "parent_product_tmpl_id": "ID_Produs_fabricat",
    "product_qty_m": "Cantitatea_Produsa",
    "product_tmpl_id": "ID_Produs",
    "product_qty": "Cantitatea_Necesara",
    "product_uom_id": "Unitatea_Masura",
}
model_search_key = {"mrp.bom": "code", "product.category": "name"}


header_bom_line_d = {
    "ready_to_produce": ("all_available", "mrp.bom"),
    "consumption": ("flexible", "mrp.bom"),
}


header_bom_line_g = {
    "code": ("Code_bom", "mrp.bom", None, None),
    "product_tmpl_id": ("ID_Produs", "mrp.bom", "product.template", [("name", None)]),
    "product_qty_1": ("Cantitate_Produsa", "mrp.bom", None, None),
    "product_id": (
        "ID_Componenta",
        "mrp.bom.line",
        "product.product",
        [("name", None)],
    ),
    "product_qty": ("Cantitate_Necesara", "mrp.bom.line", None, None),
    "product_uom_id": ("Unitatea_Masura", "mrp.bom.line", "uom.uom", [("name", None)]),
    "id": ("ID_line", "mrp.bom.line", None, None),
}

header_stock_valuation_layer_g = {
    "company_id": (
        "Compania",
        "stock.valuation.layer",
        "res.company",
        [("name", None)],
    ),
    "product_id": (
        "Product_ID",
        "stock.valuation.layer",
        "product.product",
        [("default_code", None)],
    ),
    "quantity": ("Cantitatea", "stock.valuation.layer", None, None),
    "uom_id": (
        "Unitate_de masura",
        "stock.valuation.layer",
        "product_id.uom_id",
        [("name", None)],
    ),
    "unit_cost": ("Pret", "stock.valuation.layer", None, None),
    "value": ("Value", "stock.valuation.layer", None, None),
    "description": ("Descriere", "stock.valuation.layer", None, None),
    "vechime_stoc": (
        "Vechime_stoc",
        "stock.valuation.layer",
        None,
        None,
    ),
    "depozit": (
        "Depozit",
        "stock.valuation.layer",
        None,
        None,
    ),
}

header_account_account_g = {
    "code": ("Cont", "account.account", None, None),
    "name": ("Titlu", "account.account", None, None),
    "user_type_id": (
        "Type",
        "account.account",
        "account.account.type",
        [("name", None)],
    ),
}


header_inventory = {
    "product_id": "ID_Produs",
    "location_id": "Locatie",
    "quantity": "Cantitatea",
    "available_quantity": "Cantitatea_disponibila",
    "value": "Pretul",
}

header_quant_g = {
    "product_id": ("Product_ID", "stock.quant", "product.product", [("name", None)]),
    "location_id": ("Locatie", "stock.quant", "stock.location", [("name", None)]),
    "quantity": ("Cantitatea", "stock.quant", None, None),
    "available_quantity": ("Cantitatea_disponibila", "stock.quant", None, None),
    "value": ("Pretul", "stock.quant", None, None),
}
header_inventory_g = {
    "inventory_id": (
        "Nume_inventory",
        "stock.inventory.line",
        "stock.inventory",
        [("name", "inventar_dec")],
    ),
    "product_id": (
        "Product_ID",
        "stock.inventory.line",
        "product.product",
        [("default_code", None)],
    ),
    "product_qty": ("Cantitatea", "stock.inventory.line", None, None),
    "location_id": (
        "Depozit",
        "stock.inventory.line",
        "stock.location",
        [("complete_name", None)],
    ),
    # "prod_lot_id": (
    #     "Lot",
    #     "stock.inventory.line",
    #     "stock.production.lot",
    #     [("name", None)],
    # ),
}

header_lot_g = {
    "name": ("Nume_lot", "stock.production.lot", None, None),
    "product_id": (
        "Product_id",
        "stock.production.lot",
        "product.product",
        [("default_code", None)],
    ),
    "company_id": ("Company_id", "stock.production.lot", "res.company", [("id", None)]),
}


header_asset = {
    "method": "Metoda_Amortizare",
    "method_number": "Numarul_de_Amortizari",
    "method_period": "Tipul_perioada",
    "inventory_number": "Numarul_inventar",
    "method_number_min": "Numarul_Min_amortizari",
    "method_number_max": "Numarul_Max_amortizari",
    "account_asset_id": "Contul_MijloaceFixe",
    "account_depreciation_id": "Contul_amortizari",
    "original_value": "Valoare Initiala",
    "book_value": 0,
    "value_residual": "Valoare Rezidiala",
    "first_depreciation_date": "Data_incepere_amortizare",
    "acquisition_date": "Data_achizitie",
    "already_depreciated_amount_import": "Depreciere_actuala",
    "depreciation_number_import": "Numarul_amortizari_import",
    "first_depreciation_date_import": "Data_primei_amortizari_import",
}
header_asset_g = {
    "method": "Metoda_Amortizare",
    "method_number": "Numarul_de_Amortizari",
    "method_period": "Tipul_perioada",
    "inventory_number": "Numarul_inventar",
    "method_number_min": "Numarul_Min_amortizari",
    "method_number_max": "Numarul_Max_amortizari",
    "account_asset_id": "Contul_MijloaceFixe",
    "account_depreciation_id": "Contul_amortizari",
    "original_value": "Valoare Initiala",
    "book_value": 0,
    "value_residual": "Valoare Rezidiala",
    "first_depreciation_date": "Data_incepere_amortizare",
    "acquisition_date": "Data_achizitie",
    "already_depreciated_amount_import": "Depreciere_actuala",
    "depreciation_number_import": "Numarul_amortizari_import",
    "first_depreciation_date_import": "Data_primei_amortizari_import",
}

header_product_cat = {
    "name": (
        "nume",
        "product.category",
        None,
        None,
    ),
    "parent_id": (
        "Categoria_parinte",
        "product.category",
        "product.category",
        [("name", None)],
    ),
    # "property_cost_method": 0,
    # "property_stock_account_input_categ_id": (
    #     "cont_ven",
    #     "product.category",
    #     "account.account",
    #     [("code", None)],
    # ),
    # "property_stock_account_output_categ_id": (
    #     "cont_che",
    #     "product.category",
    #     "account.account",
    #     [("code", None)],
    # ),
    # "property_stock_valuation_account_id": (
    #     "cont",
    #     "product.category",
    #     "account.account",
    #     [("code", None)],
    # ),
    # "removal_strategy_id": 0,
}


# header_product_cat = {'name': ('nume','product.category',None,None,),
#                       'parent_id': ('Categoria_parinte','product.category','product.category',[('name',None)]),
#                       'property_cost_method':0,
#                       'property_account_income_categ_id':0,
#                       'property_account_expense_categ_id':0,
#                       'property_stock_valuation_account_id':0,
#                       'removal_strategy_id': 0}

header_product = {
    "id": "id",
    "name": "Nume",
    "sequence": 0,
    "description": 0,
    "description_purchase": 0,
    "description_sale": 0,
    "categ_id": "Categorie",
    "currency_id": "",
    "cost_currency_id": 0,
    "price": "Pret",
    "list_price": 0,
    "lst_price": 0,
    "standard_price": 0,
    "volume": 0,
    "volume_uom_name": 0,
    "weight": 0,
    "weight_uom_name": 0,
    "sale_ok": "Vanzare_ok",
    "purchase_ok": "Achizitie_ok",
    "pricelist_id": 0,
    "uom_id": 0,
    "uom_name": "Unitate",
    "uom_po_id": "Unitate_achizitie",
    "company_id": 0,
    "packaging_ids": 0,
    "seller_ids": 0,
    "variant_seller_ids": 0,
    "active": 0,
    "color": 0,
    "is_product_variant": 0,
    "attribute_line_ids": 0,
    "valid_product_template_attribute_line_ids": 0,
    "product_variant_ids": 0,
    "product_variant_id": 0,
    "product_variant_count": 0,
    "barcode": "Cod_bare",
    "default_code": "SKU",
    "pricelist_item_count": 0,
    "can_image_1024_be_zoomed": 0,
    "has_configurable_attributes": 0,
    "taxes_id": "Taxe",
    "supplier_taxes_id": "Taxe_achizitie",
    "property_account_income_id": 0,
    "property_account_expense_id": 0,
    "service_type": 0,
    "sale_line_warn": 0,
    "sale_line_warn_msg": 0,
    "expense_policy": 0,
    "visible_expense_policy": 0,
    "sales_count": 0,
    "visible_qty_configurator": 0,
    "invoice_policy": 0,
    "anaf_code_id": 0,
    "image_1920": 0,
    "activity_ids": 0,
    "activity_state": 0,
    "activity_date_deadline": 0,
    "activity_exception_decoration": 0,
    "activity_exception_icon": 0,
    "message_is_follower": 0,
    "message_follower_ids": 0,
    "message_partner_ids": 0,
    "message_channel_ids": 0,
    "message_ids": 0,
    "message_unread": 0,
    "message_unread_counter": 0,
    "message_needaction": 0,
    "message_needaction_counter": 0,
    "message_has_error": 0,
    "message_has_error_counter": 0,
    "message_attachment_count": 0,
    "message_main_attachment_id": 0,
    "website_message_ids": 0,
    "message_has_sms_error": 0,
    "image_1024": 0,
    "image_512": 0,
    "image_256": 0,
    "image_128": 0,
    "activity_user_id": 0,
    "activity_type_id": 0,
    "activity_type_icon": 0,
    "activity_summary": 0,
    "responsible_id": 0,
    "type": "Tip_produs",
    "property_stock_production": 0,
    "property_stock_inventory": 0,
    "sale_delay": 0,
    "tracking": 0,
    "description_picking": 0,
    "description_pickingout": 0,
    "description_pickingin": 0,
    "qty_available": 0,
    "virtual_available": 0,
    "incoming_qty": 0,
    "outgoing_qty": 0,
    "location_id": 0,
    "warehouse_id": 0,
    "has_available_route_ids": 0,
    "route_ids": 0,
    "nbr_reordering_rules": 0,
    "reordering_min_qty": 0,
    "reordering_max_qty": 0,
    "route_from_categ_ids": 0,
    "cost_method": 0,
    "valuation": 0,
    "vendor_ids": "Furnizori",
}

header_product_g = {
    "name": ("Nume", "product.template", None, None),
    "sequence": 0,
    "description": 0,
    "description_purchase": 0,
    "description_sale": 0,
    "categ_id": ("Categorie", "product.template", "product.category", [("name", None)]),
    "currency_id": 0,
    "cost_currency_id": 0,
    "list_price": ("Pret", "product.template", None, None),
    "price": 0,
    "lst_price": 0,
    "standard_price": 0,
    "volume": 0,
    "volume_uom_name": 0,
    "weight": 0,
    "weight_uom_name": 0,
    "sale_ok": ("Vanzare_ok", "product.template", None, None),
    "purchase_ok": ("Achizitie_ok", "product.template", None, None),
    "pricelist_id": 0,
    "uom_id": ("Unitate", "product.template", "uom.uom", [("name", None)]),
    "uom_name": 0,
    "uom_po_id": ("Unitate_achizitie", "product.template", "uom.uom", [("name", None)]),
    "company_id": 0,
    "packaging_ids": 0,
    "seller_ids": 0,
    "variant_seller_ids": 0,
    "active": 0,
    "color": 0,
    "is_product_variant": 0,
    "attribute_line_ids": 0,
    "valid_product_template_attribute_line_ids": 0,
    "product_variant_ids": 0,
    "product_variant_id": 0,
    "product_variant_count": 0,
    "barcode": 0,
    "default_code": ("Descriere", "product.template", None, None),
    "pricelist_item_count": 0,
    "can_image_1024_be_zoomed": 0,
    "has_configurable_attributes": 0,
    "taxes_id": ("Taxe", "product.template", "account.tax", [("name", None)]),
    "supplier_taxes_id": (
        "Taxe_achizitie",
        "product.template",
        "account.tax",
        [("name", None)],
    ),
    "property_account_income_id": 0,
    "property_account_expense_id": 0,
    "service_type": 0,
    "sale_line_warn": 0,
    "sale_line_warn_msg": 0,
    "expense_policy": 0,
    "visible_expense_policy": 0,
    "sales_count": 0,
    "visible_qty_configurator": 0,
    "invoice_policy": 0,
    "anaf_code_id": 0,
    "image_1920": 0,
    "activity_ids": 0,
    "activity_state": 0,
    "activity_date_deadline": 0,
    "activity_exception_decoration": 0,
    "activity_exception_icon": 0,
    "message_is_follower": 0,
    "message_follower_ids": 0,
    "message_partner_ids": 0,
    "message_channel_ids": 0,
    "message_ids": 0,
    "message_unread": 0,
    "message_unread_counter": 0,
    "message_needaction": 0,
    "message_needaction_counter": 0,
    "message_has_error": 0,
    "message_has_error_counter": 0,
    "message_attachment_count": 0,
    "message_main_attachment_id": 0,
    "website_message_ids": 0,
    "message_has_sms_error": 0,
    "image_1024": 0,
    "image_512": 0,
    "image_256": 0,
    "image_128": 0,
    "activity_user_id": 0,
    "activity_type_id": 0,
    "activity_type_icon": 0,
    "activity_summary": 0,
    "responsible_id": 0,
    "type": ("Tip_produs", "product.template", None, None),
    "property_stock_production": 0,
    "property_stock_inventory": 0,
    "sale_delay": 0,
    "tracking": 0,
    "description_picking": 0,
    "description_pickingout": 0,
    "description_pickingin": 0,
    "qty_available": 0,
    "virtual_available": 0,
    "incoming_qty": 0,
    "outgoing_qty": 0,
    "location_id": 0,
    "warehouse_id": 0,
    "has_available_route_ids": 0,
    "route_ids": 0,
    "nbr_reordering_rules": 0,
    "reordering_min_qty": 0,
    "reordering_max_qty": 0,
    "route_from_categ_ids": 0,
    "cost_method": 0,
    "valuation": 0,
    "vendor_ids": 0,
}
header_product_cost_g = {
    "default_code": ("Cod", "product.template", None, None),
    "standard_price": ("Cost", "product.template", None, None),
}


header_partner = {
    "id": "Id",
    "name": "Nume",
    "parent_id": "Parinte",
    "vat": "CUI",
    "type": 0,
    "street": "Adresa",
    "street2": "Adresa2",
    "zip": "Cod_postal",
    "city": "Oras",
    "state_id": "Judet",
    "country_id": "Tara",
    "is_company": "Este_companie",
    "email": "Email",
    "phone": "Telefon",
    "bank_id": "Banca",
    "acc_number": "Numar_cont",
}

header_partner_g = {
    "name": ("Nume", "res.partner", False, None),
    "parent_id": 0,
    "vat": ("CUI", "res.partner", None, None),
    "type": 0,
    "street": ("Adresa", "res.partner", None, None),
    "street2": ("Adresa2", "res.partner", None, None),
    "zip": ("Cod_postal", "res.partner", None, None),
    "city": ("Oras", "res.partner", None, None),
    "state_id": (
        "Judet",
        "res.partner",
        "res.country.state",
        [("code", None), ("country_id", "country_id")],
    ),
    "country_id": ("Tara", "res.partner", "res.country", [("name", None)]),
    "is_company": ("Este_companie", "res.partner", None, None),
    "email": ("Email", "res.partner", None, None),
    "phone": ("Telefon", "res.partner", None, None),
    # 'bank_id':('Banca','res.partner.bank','res.bank','name'),
    # 'acc_number':('Numar_cont','res.partner.bank',None,None)
}
header_partner_d = {"is_company": (True, "res.partner")}

header_account_move = {}
header_account = {
    "code": "Cont",
    "opening_debit": "Debit_initial",
    "opening_credit": "Credit_initial",
    "opening_balance": "Balanta_initiala",
    "opening_balance_currency": "Balanta_initiala_moneda",
    "currency_id": "Moneda",
}


header_account_g = {
    "account_id": ("Cont", "account.move.line", "account.account", [("code", None)]),
    "debit": ("Debit_initial", "account.move.line", None, None),
    "credit": ("Credit_initial", "account.move.line", None, None),
    # 'opening_balance': ('Balanta_initiala','account.account',None,None),
    "balance": ("Balanta_initiala_moneda", "account.move.line", None, None),
    "currency_id": ("Moneda", "account.move.line", "res.currency", [("name", None)]),
    "state": ("State", "account.move", None, None),
    "date": ("data", "account.move", None, None),
    "ref": ("ref", "account.move", None, None),
}


header_move_line = {
    "account_id": "Cont",
    "partner_id": "ID_partener",
    "move_id": "Nr_factura",
    "debit": "debit",
    "credit": "credit",
    "balance": "balance",
    "invoice_date_due": "data_scadenta",
}
header_move_line_g = {
    "account_id": ("Cont", "account.move.line", "account.account", [("code", None)]),
    "partner_id": ("ID_partener", "account.move.line", "res.partner", [("name", None)]),
    "debit": ("Debit", "account.move.line", None, None),
    "credit": ("Credit", "account.move.line", None, None),
    "amount_currency": ("Balanta_valuta", "account.move.line", None, None),
    "currency_id": ("Valuta", "account.move.line", "res.currency", [("name", None)]),
    "date_maturity": ("Data_scadenta", "account.move.line", None, None),
    "date": ("data", "account.move.line", None, None),
    # "date_1": ("Data_Move", "account.move", None, None),
    "move_type": ("tipul_facturi", "account.move", None, None),
    "state": ("State", "account.move", None, None),
    "ref": ("ref", "account.move", None, None),
    "name": ("label", "account.move.line", None, None),
}


header_move_account = {
    "id": "id",
    "sequence_number": "Numar",
    "sequence_prefix": "Serie",
    "date": "data",
    "move_type": "tipul_facturi",
    "partner_id": "partener",
    "partner_bank_id": "banca_partenerului",
    "fiscal_position_id": "regimul_fiscal",
    "invoice_date": "data_facturii",
    "invoice_date_due": "data_scadenta",
    "amount_untaxed": "total_fara_taxe",
    "amount_tax": "total_taxe",
    "amount_total": "total_cu_taxe",
    "amount_residual": 0,
    "amount_untaxed_signed": 0,
}
# Nume,Numar_inventar,Model,Grup,Data_achizitie,Data_amortizare,Data_amortizare_import,Valoare_initiala,Valoare_amortizare,Numar_amortizari,Numar_amortizari_import,Cont_mijloc_fix,Cont_amortizari,Cont_cheltuiala
header_asset_g = {
    "name": ("Nume", "account.asset", None, None),
    "model": ("Model", "account.asset", None, None),
    "method": ("Metoda_Amortizare", "account.asset", None, None),
    "method_number": ("Numar_amortizari", "account.asset", None, None),
    "method_period": ("Tipul_perioada", "account.asset", None, None),
    "group_id": ("Grup", "account.asset", "account.asset.group", [("code", None)]),
    "inventory_number": ("Numar_inventar", "account.asset", None, None),
    # "method_number_min":( "Numarul_Min_amortizari",'account.asset',None,None),
    # "method_number_max": ("Numarul_Max_amortizari",'account.asset',None,None),
    "account_asset_id": (
        "Cont_mijloc_fix",
        "account.asset",
        "account.account",
        [("code", None)],
    ),
    "account_depreciation_id": (
        "Cont_amortizari",
        "account.asset",
        "account.account",
        [("code", None)],
    ),
    "account_depreciation_expense_id": (
        "Cont_cheltuiala",
        "account.asset",
        "account.account",
        [("code", None)],
    ),
    "journal_id": ("Jurnal", "account.asset", "account.journal", [("code", None)]),
    "original_value": ("Valoare_initiala", "account.asset", None, None),
    "book_value": 0,
    "value_residual": 0,
    "first_depreciation_date": ("Data_amortizare", "account.asset", None, None),
    "acquisition_date": ("Data_achizitie", "account.asset", None, None),
    "already_depreciated_amount_import": (
        "Valoare_amortizare",
        "account.asset",
        None,
        None,
    ),
    "depreciation_number_import": (
        "Numar_amortizari_import",
        "account.asset",
        None,
        None,
    ),
    "first_depreciation_date_import": (
        "Data_amortizare_import",
        "account.asset",
        None,
        None,
    ),
    "state": ("State", "account.asset", None, None),
    "asset_type": ("Tip", "account.asset", None, None),
}
