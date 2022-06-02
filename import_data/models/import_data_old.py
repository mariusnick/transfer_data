# Copyright 2021 NextERP Romania SRL
# License OPL-1.0 or later
# (https://www.odoo.com/documentation/user/14.0/legal/licenses/licenses.html#).

import csv
import logging
import os

from odoo import fields, models

_logger = logging.getLogger(__name__)

from .dict_fields import (
    header_account_g,
    header_asset_g,
    header_bom_line_g,
    header_inventory_g,
    header_move_line_g,
    header_partner_d,
    header_partner_g,
    header_product_cat,
    header_product_g,
)


class ImportData(models.Model):
    _name = "import.data"
    _description = "Import data in models"

    time_import = fields.Datetime(readonly=True, default=fields.Datetime.now())
    file_import = fields.Selection(
        string="File/Model Import",
        selection=[
            ("partner", "Partners"),
            ("cat_product", "Category Product"),
            ("product", "Product"),
            ("account", "Initial Balance"),
            ("balance_partner", "Balance Partner"),
            ("bom", "Bom"),
            ("asset", "Asset"),
            ("inventory", "Inventory"),
            ("valuation", "Stock_valuation"),
        ],
        default="partner",
    )

    update_data = fields.Boolean(string="Update", default=True)
    details = fields.Html(
        "Import details", help="Contains details and errors in the import process "
    )
    check = fields.Boolean(string="Check", default=False)

    def inverse_dict(self, my_dict):
        res = {}
        for key, value in my_dict.items():
            res[value] = key
        return res

    def get_path(self, file_name):
        os.chdir("..")
        os.chdir("..")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

        path_parent = os.path.dirname(path)
        path_parent_grand = os.path.dirname(path_parent)

        os.chdir(path_parent)

        path_data = os.path.join(path_parent_grand, "import_initial", file_name)
        _logger.info(f"Reading file:{path_parent}")
        return path_data

    def inverse_dict1(self, my_dict):
        res = {}
        for key, value in my_dict.items():
            _logger.warning(value)
            if value != 0:
                t, m, cm, f = value
                res[t] = key
        return res

    def translate_double_key(self, keyss):
        if keyss[-2:] == "_1":
            keyss = keyss[:-2]
        return keyss

    def merge_models(self, models_string, record_field, rel_keys=[], check=False):
        # Find out if it is a record created in the database,
        # if yes it returns it with the one from the basic model,
        # if it does not create it and returns it
        domain = []
        for rkeys, rvalue in rel_keys:
            domain.append((rkeys, "=", rvalue))
        item = self.env[models_string].search(domain, limit=1)

        _logger.warning(f"{models_string},{domain}")
        _logger.warning(item)
        res = None
        mess = None
        if item:
            res = item
            _logger.warning(f"For {models_string} find {item.id} ")
        else:
            vals = {rkeys: rvalue for (rkeys, rvalue) in rel_keys}
            if not check:
                res = self.env[models_string].create(vals)
                _logger.warning(f"For {models_string}  Create {item.id} ")
            else:
                _logger.warning("NNNNNNXXXXXXXXXXXXXXXXXXNNNNN")
                _logger.warning(f"No Found {domain}, in model {models_string}")
                mess = f"No Found {domain}, in model {models_string} \n"
                mess = mess + "455"

        return res, mess

    def import_model(self):
        _logger.warning(self.check)
        if not self.check:
            if self.file_import == "partner":
                # self.import_partners()
                self.import_generic_models(
                    "partner.csv", header_partner_g, None, header_partner_d
                )
            elif self.file_import == "cat_product":
                self.import_generic_models("categorii_produse.csv", header_product_cat)

            elif self.file_import == "account":
                self.import_generic_models("account_template.csv", header_account_g, 1)
            elif self.file_import == "product":
                self.import_generic_models("produse.csv", header_product_g)
                # self.update_product_models('produse.csv','description',header_product_g)
                # self.export_generic_models('produse.csv',header_product_g)
                # self.update_product1_models('valuation.csv',header_product_g)

            elif self.file_import == "inventory":
                self.import_generic_models("inventory.csv", header_inventory_g)

            elif self.file_import == "bom":
                self.import_generic_models("bom_line.csv", header_bom_line_g)
            elif self.file_import == "balance_partner":
                self.import_generic_models(
                    "account_move_partner.csv", header_move_line_g, 1
                )
            elif self.file_import == "asset":
                self.import_generic_models("asset.csv", header_asset_g)
            elif self.file_import == "valuation":
                self.update_valuation_models("valuation.csv")
                # self.empty_model_stock_evaluation()

                # quants = self.env['stock.quant'].sudo().search([('])
                # quants._compute_value()

        else:

            if self.file_import == "inventory":
                _logger.warning("Mark1")
                self.check_id_link("inventory.csv", header_inventory_g)
            if self.file_import == "bom":
                _logger.warning("Mark1")
                self.check_id_link("bom_line.csv", header_bom_line_g)

    def get_field_merge(self, model_level, model, item_dict):
        #
        res = {}

        ir_model_obj = self.env["ir.model.fields"]
        if model != model_level[1][0]:
            ir_model_field = ir_model_obj.search(
                [("model", "=", model), ("relation", "=", model_level[1][0])], limit=1
            )

            item = item_dict[model_level[1][0]]
            res[ir_model_field.name] = item.id
        else:

            for model_rel in item_dict.keys():
                if model_rel in model_level[0]:
                    ir_model_field = ir_model_obj.search(
                        [("model", "=", model), ("relation", "=", model_rel)], limit=1
                    )
                    item = item_dict[model_rel]
                    res[ir_model_field.name] = item.id

        return res

    def order_models(self, header_generic):
        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        models = []
        for keyss, values in header_generic.items():
            if values != 0:
                t, m, cm, f = values
                models.append(m)
        _logger.warning(models)
        models_uniq = []
        for x in models:
            if x not in models_uniq:
                models_uniq.append(x)
        models = models_uniq
        model_baza = models[0]

        model_rel_keys = {}
        model_rel = [[] for i in range(3)]
        _logger.warning(model_rel)
        model_rel[1].append(model_baza)
        ir_model_obj = self.env["ir.model.fields"]
        for model in models[1:]:
            ir_model_field = ir_model_obj.search([("model", "=", model)])
            rel = []

            for field in ir_model_field:
                if field.relation:
                    if field.relation == model_baza:
                        rel.append((field.name, field.relation))
                        model_rel_keys[model] = rel
                        if field.ttype == "many2one":
                            if model not in model_rel[2]:
                                model_rel[2].append(model)

        ir_model_field = ir_model_obj.search([("model", "=", model_baza)])
        rel = []

        for field in ir_model_field:
            if field.relation:
                if field.relation in models[1:]:
                    rel.append((field.name, field.relation))
                    if field.ttype == "many2one":
                        if field.relation not in model_rel[0]:
                            model_rel[0].append(field.relation)
                    model_rel_keys[model_baza] = rel

        return model_rel, model_rel_keys

    def convert_type_field(self, dict_filter, model):
        for field, value in dict_filter.items():
            field_db = self.env["ir.model.fields"].search(
                [("model", "=", model), ("name", "=", field)]
            )

            if field_db.ttype == "monetary" or field_db.ttype == "float":
                _logger.warning(f"Convert {field}")
                dict_filter[field] = float(value)
        return dict_filter

    def import_generic_models(
        self, file_name, header_generic, level_multiline=None, default_model=None
    ):
        headear_inv = self.inverse_dict1(header_generic)
        details = []
        models = []
        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        model_level, model_rel_keys = self.order_models(header_generic)

        for keyss, values in header_generic.items():
            if values != 0:
                t, m, cm, f = values
                models.append(m)

        models_uniq = []
        for x in models:
            if x not in models_uniq:
                models_uniq.append(x)
        models = models_uniq

        keys_models = {}
        for model in models:
            keys_model = []
            for keyss, values in header_generic.items():
                t, m, cm, f = values
                if m == model:
                    if keyss[-2:] == "_1":
                        keyss = keyss[:-2]
                    keys_model.append(keyss)
            keys_models[model] = keys_model
        details.append("<div> Reading file:{}</div>".format(self.get_path(file_name)))
        if level_multiline:
            items_create = {model: [] for model in model_level[level_multiline]}

        with open(self.get_path(file_name), "r") as infile:
            reader = csv.reader(infile)
            headers = next(reader)[0:]

            headers_translate = [headear_inv[h] for h in headers]

            _logger.warning("Mark1")
            _logger.warning(headers)
            _logger.warning(headear_inv)
            _logger.warning(headers_translate)
            _logger.warning(keys_models)
            item_dict = {}
            # _logger.warning(f"numarul de randuri{len(list(reader))}")
            for row in reader:
                _logger.warning("Mark2")
                if len(headers_translate) != len(row):
                    _logger.warning(
                        f"The number of headers fields  does not match the number of fields in the row number {row}"
                    )
                if 1 == 1:
                    dict_read = {
                        key: (value) for key, value in zip(headers_translate, row[0:])
                    }
                    _logger.warning(dict_read)
                    for level, models in enumerate(model_level):
                        _logger.warning(models)
                        for model in models:
                            _logger.warning(f"an object of type{model} is created")
                            # _logger.warning(keys_models)
                            keys_model = keys_models[model]
                            # _logger.warning('Model keys')
                            # _logger.warning(keys_model)
                            # _logger.warning('Dict 0000')
                            # se selecteaza campurile din dic_read care sunt in model
                            dict_filter_00 = {
                                k: dict_read[k]
                                for k, v in header_generic.items()
                                if v[1] == model and k in dict_read.keys()
                            }
                            _logger.warning(dict_filter_00)
                            # se transforma campul cu _1 ( care apare in mai multe modele) cu denumirea campului din model
                            dict_filter_0 = {
                                self.translate_double_key(k): value
                                for k, value in dict_filter_00.items()
                            }

                            _logger.warning(dict_filter_0)
                            # se verifica daca campurile sunt in model ( luat din odoo) si sa nu fie nule
                            dict_filter_1 = {
                                k: dict_filter_0[k]
                                for k in keys_model
                                if k in dict_filter_0 and dict_filter_0[k]
                            }
                            # _logger.warning("Dict Filter")
                            # _logger.warning(dict_filter_1)
                            search_key = None
                            for keyss, values in header_generic.items():
                                t, m, cm, f = values
                                if keyss in dict_filter_1.keys():
                                    if cm:
                                        # Merge link id model
                                        ir_model_obj = self.env["ir.model.fields"]
                                        ir_model_field = ir_model_obj.search(
                                            [("model", "=", m), ("name", "=", keyss)],
                                            limit=1,
                                        )
                                        _logger.warning(
                                            f"{keyss}:{ir_model_field.ttype}"
                                        )
                                        if (
                                            ir_model_field.ttype == "many2one"
                                            or "many2many"
                                        ):
                                            if f:
                                                rel_keys = []
                                                _logger.warning(f)
                                                for ritems in f:
                                                    rkeys, rvalue = ritems

                                                    if rvalue == None:

                                                        rvalue = dict_filter_1[keyss]
                                                        rel_keys.append((rkeys, rvalue))
                                                    else:
                                                        if (
                                                            rvalue
                                                            in dict_filter_1.keys()
                                                        ):

                                                            rel_keys.append(
                                                                (
                                                                    rkeys,
                                                                    dict_filter_1[
                                                                        rvalue
                                                                    ],
                                                                )
                                                            )
                                                        else:
                                                            rel_keys.append(
                                                                (rkeys, rvalue)
                                                            )

                                                item_object, mess = self.merge_models(
                                                    cm, dict_filter_1[keyss], rel_keys
                                                )

                                            _logger.warning(f"Merge {keyss}")
                                        if ir_model_field.ttype == "many2one":
                                            dict_filter_1[keyss] = item_object.id
                                        elif ir_model_field.ttype == "many2many":
                                            dict_filter_1[keyss] = [(4, item_object.id)]
                                    else:
                                        if f:
                                            search_key = keyss, f
                            if level > 0:
                                field_merge = self.get_field_merge(
                                    model_level, model, item_dict
                                )
                                _logger.warning(field_merge)
                                dict_filter_1.update(field_merge)
                            # insert default value
                            if default_model:
                                for dkeys in default_model.keys():
                                    if default_model[dkeys][1] == model:
                                        if dkeys in dict_filter_1.keys():
                                            if not dict_filter_1[dkeys]:
                                                dict_filter_1[dkeys] = default_model[
                                                    dkeys
                                                ][0]
                                        else:
                                            dict_filter_1[dkeys] = default_model[dkeys][
                                                0
                                            ]

                            # _logger.warning(dict_filter_1.keys())
                            # _logger.warning(header_default.keys())
                            # dict_filter_1.update(header_default[model])
                            _logger.warning("Mark5")

                            dict_filter_1 = self.convert_type_field(
                                dict_filter_1, model
                            )
                            _logger.warning(dict_filter_1)
                            if 1 == 1:
                                if search_key:
                                    keyss, f = search_key
                                    if 1 == 1:
                                        rel_keys = []
                                        _logger.warning(f)
                                        for ritems in f:
                                            rkeys, rvalue = ritems
                                            _logger.warning("Initial")
                                            _logger.warning(f"{rkeys}:{rvalue}")
                                            if rvalue == None:
                                                _logger.warning(
                                                    "Latura None, get value"
                                                )
                                                rvalue = dict_filter_1[keyss]
                                                rel_keys.append((rkeys, rvalue))
                                            else:
                                                if rvalue in dict_filter_1.keys():

                                                    rel_keys.append(
                                                        (rkeys, dict_filter_1[rvalue])
                                                    )
                                                else:
                                                    rel_keys.append((rkeys, rvalue))
                                        _logger.warning("RREl Keys")
                                        _logger.warning(rel_keys)

                                    domain = []
                                    for rkeys, rvalue in rel_keys:
                                        domain.append((rkeys, "=", rvalue))

                                    item_search = self.env[model].search(
                                        domain, limit=1
                                    )

                                else:
                                    ir_model_obj = self.env["ir.model.fields"]
                                    ir_model_field = ir_model_obj.search(
                                        [("model", "=", model)]
                                    )

                                    domain = []

                                    dict_filter_str_float = []
                                    for field in ir_model_field:

                                        if field.name in dict_filter_1.keys():
                                            if field.ttype in [
                                                "char",
                                                "text",
                                                "integer",
                                                "float",
                                                "boolean",
                                                "monetary",
                                                "selection",
                                            ]:
                                                dict_filter_str_float.append(field.name)

                                    for field in dict_filter_str_float:
                                        domain.append(
                                            (field, "=", dict_filter_1[field])
                                        )
                                    _logger.warning(domain)
                                    item_search = self.env[model].search(
                                        domain, limit=1
                                    )

                                if item_search and level < 2:
                                    item_dict[model] = item_search
                                    _logger.warning(
                                        f" Find {model}:{item_search} dont create new item"
                                    )
                                else:
                                    if level != level_multiline:
                                        _logger.warning("MMMarkf")
                                        _logger.warning(dict_filter_1)
                                        item_dict[model] = (
                                            self.env[model].sudo().create(dict_filter_1)
                                        )
                                        _logger.warning(
                                            f"Create new item {model} id{item_dict[model].id}"
                                        )
                                    else:
                                        items_create[model].append(dict_filter_1)
                                    _logger.warning(
                                        f"Was create obj{model}:{item_search}"
                                    )

                                _logger.warning(item_dict)
                # except Exception as e:
                #     list_fail += e
                #     _logger.warning(e)
        if level_multiline:
            for model in items_create.keys():
                _logger.warning(items_create[model])
                self.env[model].sudo().create(items_create[model])

        return True

    def update_generic_models(
        self, file_name, field_search, header_generic, extra_string=None
    ):
        headear_partener_inv = self.inverse_dict1(header_generic)

        models = []
        header_generic = {key: val for key, val in header_generic.items() if val != 0}

        for keyss, values in header_generic.items():
            if values != 0:
                t, m, cm, f = values
                _logger.warning(f"Model {m}")
                models.append(m)
        models = list(set(models))
        _logger.warning(models)

        keys_models = []
        for model in models:
            keys_model = []
            for keyss, values in header_generic.items():
                t, m, cm, f = values
                if m == model:
                    keys_model.append(keyss)
            keys_models.append(keys_model)

        _logger.warning(keys_models)
        keys_models[0].remove(field_search)

        with open(self.get_path(file_name), "r") as infile:
            reader = csv.reader(infile)
            headers = next(reader)[0:]
            _logger.warning(headers)
            headers_translate = [headear_partener_inv[h] for h in headers]
            _logger.warning(headers_translate)
            _logger.warning(keys_models)
            for row in reader:
                dict_read = {
                    key: (value) for key, value in zip(headers_translate, row[0:])
                }
                value_search = extra_string + dict_read[field_search]
                field_update = self.env[models[0]].search(
                    [(field_search, "=", value_search)]
                )
                dict_filter_1 = {
                    k: dict_read[k] for k in keys_models[0] if k in dict_read
                }
                _logger.warning(dict_filter_1)
                for keyss, values in header_generic.items():
                    t, m, cm, f = values
                    if keyss in keys_models[0]:
                        if cm:
                            _logger.warning(cm)
                            item_object = self.merge_models(cm, dict_filter_1[keyss], f)
                            dict_filter_1[keyss] = item_object.id
                field_update.write(dict_filter_1)

        return True

    def check_id_link(
        self, file_name, header_generic, level_multiline=None, default_model=None
    ):
        # Pentru idmodel verifica daca exista itemul de care vrem sa ne legam sau trebuie creat, prin acesta verificam
        # daca sunt regasite anumite obiecte care au fost create anterior
        headear_inv = self.inverse_dict1(header_generic)

        models = []
        list_fail = []
        string_details = ""
        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        model_level, model_rel_keys = self.order_models(header_generic)

        for keyss, values in header_generic.items():
            if values != 0:
                t, m, cm, f = values
                models.append(m)

        models_uniq = []
        for x in models:
            if x not in models_uniq:
                models_uniq.append(x)
        models = models_uniq

        keys_models = {}
        for model in models:
            keys_model = []
            for keyss, values in header_generic.items():

                t, m, cm, f = values
                if m == model:
                    if keyss[-2:] == "_1":
                        keyss = keyss[:-2]
                    keys_model.append(keyss)
            keys_models[model] = keys_model
        string_details += "<div> Reading file:{}</div>".format(self.get_path(file_name))
        if level_multiline:
            items_create = {model: [] for model in model_level[level_multiline]}

        with open(self.get_path(file_name), "r") as infile:
            reader = csv.reader(infile)
            headers = next(reader)[0:]

            headers_translate = [headear_inv[h] for h in headers]
            _logger.warning("Mark1")
            _logger.warning(headers)
            _logger.warning(headear_inv)
            _logger.warning(headers_translate)
            _logger.warning(keys_models)
            number_row = 1
            # _logger.warning(f"numarul de randuri{len(list(reader))}")
            for row in reader:
                _logger.warning("Mark2")
                if len(headers_translate) != len(row):
                    _logger.warning(
                        f"The number of headers fields  does not match the number of fields in the row number {row}"
                    )
                if 1 == 1:

                    dict_read = {
                        key: (value) for key, value in zip(headers_translate, row[0:])
                    }
                    _logger.warning(dict_read)
                    for level, models in enumerate(model_level):

                        for model in models:

                            # _logger.warning(keys_models)
                            keys_model = keys_models[model]
                            # _logger.warning('Model keys')
                            # _logger.warning(keys_model)
                            # _logger.warning('Dict 0000')
                            # se selecteaza campurile din dic_read care sunt in model
                            dict_filter_00 = {
                                k: dict_read[k]
                                for k, v in header_generic.items()
                                if v[1] == model and k in dict_read.keys()
                            }

                            # se transforma campul cu _1 ( care apare in mai multe modele) cu denumirea campului din model
                            dict_filter_0 = {
                                self.translate_double_key(k): value
                                for k, value in dict_filter_00.items()
                            }

                            # se verifica daca campurile sunt in model ( luat din odoo) si sa nu fie nule
                            dict_filter_1 = {
                                k: dict_filter_0[k]
                                for k in keys_model
                                if k in dict_filter_0 and dict_filter_0[k]
                            }
                            # _logger.warning("Dict Filter")
                            # _logger.warning(dict_filter_1)
                            for keyss, values in header_generic.items():
                                t, m, cm, f = values
                                if keyss in dict_filter_1.keys():
                                    if cm:
                                        # Merge link id model
                                        ir_model_obj = self.env["ir.model.fields"]
                                        ir_model_field = ir_model_obj.search(
                                            [("model", "=", m), ("name", "=", keyss)],
                                            limit=1,
                                        )
                                        _logger.warning(
                                            f"{keyss}:{ir_model_field.ttype}"
                                        )
                                        if ir_model_field.ttype == "many2one":
                                            if f:
                                                rel_keys = []
                                                for ritems in f:
                                                    rkeys, rvalue = ritems
                                                    if rvalue == None:
                                                        rvalue = dict_filter_1[keyss]
                                                        rel_keys.append((rkeys, rvalue))
                                                    else:
                                                        if (
                                                            rvalue
                                                            in dict_filter_1.keys()
                                                        ):

                                                            rel_keys.append(
                                                                (
                                                                    rkeys,
                                                                    dict_filter_1[
                                                                        rvalue
                                                                    ],
                                                                )
                                                            )
                                                        else:
                                                            rel_keys.append(
                                                                (rkeys, rvalue)
                                                            )

                                                item_object, mess = self.merge_models(
                                                    cm,
                                                    dict_filter_1[keyss],
                                                    rel_keys,
                                                    check=True,
                                                )
                                                if mess:
                                                    string_details += f"<div>In Row Number {number_row}</div>"
                                                    string_details += mess
                                                    list_fail.append(mess)

                number_row += 1
        self.details = str(string_details)
        # _logger.warning(list_fail[0])
        return True

    def export_generic_models(self, file_name, header_generic):

        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        model_level, model_rel_keys = self.order_models(header_generic)
        file_name = "XXX.csv"
        _logger.warning(model_level)
        with open(self.get_path(file_name), mode="w") as csv_file:
            fieldnames = [val[0] for val in header_generic.values()]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            if len(model_level[2]) > 0:
                model_write = model_level[2][0]
            if len(model_level[1]) > 0:
                model_write = model_level[1][0]
            values_write = self.env[model_write].search([])
            self.env[model_write]
            # models_ids = self.env['product.template'].search([('id', '=', rule.product_id.id)])
            # for val in values_write:
            #     new_dict = val.read(list(set(model_obj._fields)))
            #     _logger.warning(new_dict)
            new_dict = {}
            ir_model_obj = self.env["ir.model.fields"]

            model_write_field = ir_model_obj.search([("model", "=", model_write)])
            for val in values_write:
                for field in model_write_field:
                    if field.store:
                        if field.ttype not in ["many2one", "many2many", "one2many"]:
                            new_dict[field.name] = val[field.name]

                        elif field.ttype in ["many2one", "many2many"]:

                            if field.name in header_generic.keys():
                                if header_generic[field.name] != 0:
                                    t, m, cm, f = header_generic[field.name]
                                    name_field_rel, val_rel = f[0]
                                    _logger.warning(val[field.name])
                                    val_rel_found = self.env[cm].search(
                                        [("id", "=", val[field.name].id)]
                                    )
                                    if field.ttype == "many2one":
                                        _logger.warning(val_rel_found[name_field_rel])
                                        _logger.warning(field.name)
                                        new_dict[field.name] = val_rel_found[
                                            name_field_rel
                                        ]
                                    else:
                                        _logger.warning(field.name)
                                        _logger.warning(val_rel_found[name_field_rel])
                                        new_dict[field.name] = val_rel_found[
                                            name_field_rel
                                        ]

                _logger.warning("Newdict")
                _logger.warning(new_dict)
                nnew_dict = {}
                for keyy in header_generic.keys():
                    if header_generic[keyy] != 0:
                        nnew_dict[header_generic[keyy][0]] = new_dict[keyy]

                writer.writerow(nnew_dict)

    def empty_model_stock_evaluation(self):
        record_set = self.env["stock.valuation.layer"].search([])
        record_set.sudo().unlink()
