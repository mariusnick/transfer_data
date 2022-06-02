# Copyright 2022 OEC
# License OPL-1.0 or later
# (https://www.odoo.com/documentation/user/14.0/legal/licenses/licenses.html#).

import base64
import csv
import logging
import os
from datetime import datetime
from io import StringIO

from odoo import api, fields, models, _
from odoo.tests import Form
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

from .dict_fields import (
    header_account_account_g,
    header_account_g,
    header_asset_g,
    header_bom_line_g,
    header_inventory_g,
    header_lot_g,
    header_move_line_g,
    header_partner_d,
    header_partner_g,
    header_product_cat,
    header_product_g,
    header_stock_valuation_layer_g,
)


# header_stock_valuation_layer_d


def correct_value(val, type):
    if type != 'boolean' and val is False:
        return ''
    else:
        return val


class ImportData(models.Model):
    _name = "import.data"
    _description = "Import data in models"

    attachment_ids = fields.Many2many('ir.attachment', string='Files', required=True,
                                      help='Get import File')

    time_import = fields.Datetime(readonly=True, default=fields.Datetime.now())

    update_data = fields.Boolean(string="Update", default=True)
    details = fields.Html(
        "Import details", help="Contains summary and errors in the import process "
    )
    check = fields.Boolean(string="Check", default=True)
    dict_import_id = fields.Many2one('import.dict', string='Import dictinary')

    choose_file = fields.Binary(help="Select CSV file to download.")
    file_name = fields.Char(help="Name of CSV file.")

    def import_file(self):
        """ return file  """
        self.ensure_one()
        statement_ids_all = []
        statement_line_ids_all = []
        notifications_all = []
        for data_file in self.attachment_ids:
            _logger.warning('data_file')
        return self.attachment_ids[0]

    def inverse_dict(self, my_dict):
        res = {}
        for key, value in my_dict.items():
            res[value] = key
        return res

    def get_path(self, file_name, folder="import_initial"):
        os.chdir("..")
        os.chdir("..")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        path_parent = os.path.dirname(path)
        path_parent_grand = os.path.dirname(path_parent)

        os.chdir(path_parent)

        path_data = os.path.join(path_parent_grand, folder, file_name)

        _logger.info(f"Reading file from:{path_parent_grand}")
        return path_data

    def inverse_dict1(self, my_dict):
        res = {}
        _logger.warning(f'Dict receive {my_dict}')

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

    def merge_models(self, models_string, rel_keys=[], check=False):
        # Find out if it is a record created in the database,
        # if yes it returns it with the one from the basic model,
        # if it does not create it and returns it
        domain = []
        _logger.warning(rel_keys)
        for rkeys, rvalue in rel_keys:
            domain.append((rkeys, "=", rvalue))
        _logger.warning(domain)
        item = self.env[models_string].search(domain, limit=1)

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
                _logger.warning(f"No Found {domain}, in model {models_string}")
                mess = f"No Found {domain}, in model {models_string} \n"
                mess = mess + "455"

        return res, mess

    files_name = {
        "partner": ("partner.csv", header_partner_g),
        "cat_product": ("cat_exp.csv", header_product_cat),
        "account": ("account_dec.csv", header_account_g),
        "product": ("product2.csv", header_product_g),
        "inventory": ("inventory4.csv", header_inventory_g),
        "bom": ("bom_line.csv", header_bom_line_g,),
        "balance_partner": ("account_move_partner.csv", header_move_line_g),
        "asset": ("asset.csv",),
        "valuation": ("valuation_obj.csv", header_stock_valuation_layer_g),
    }

    def check_data(self):
        header_generic = self.dict_import_id.get_dict()
        default_model = self.dict_import_id.get_dict_default()
        file_name = self.dict_import_id.file_name_import_default
        summary = []
        error_mess = []
        error_mess = self.dict_import_id.chek_model()
        error = [True]
        if self.attachment_ids:
            data_file = self.import_file()
            csv_data = base64.b64decode(data_file.datas)
            data_file = StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)
            headers = file_reader[0]
            reader = file_reader[1:]
            summary.append("<div> Reading file:{}</div>".format(self.attachment_ids[0].name))
        else:
            if file_name:
                file_reader = []
                summary.append("<div> Reading file:{}</div>".format(self.get_path(file_name)))
                with open(self.get_path(file_name), "r") as infile:
                    reader = csv.reader(infile)
                    headers = next(reader)[0:]
                    for row in reader:
                        file_reader.append(row)
                        reader = file_reader
            else:
                raise UserError(_("No file ."))

        number_col = len(headers)
        summary.append("<div> Number coloms in file:{}</div>".format(len(headers)))
        summary.append(("<div> Number rows in file:{}</div>".format(len(reader))))
        # check headers
        headers_generic_name = [field[0] for field in header_generic.values()]
        fields_missing = [f for f in headers if f not in headers_generic_name]
        fields_plus = [f for f in headers_generic_name if f not in headers]
        _logger.warning("CHECK >>>>")
        _logger.warning(fields_missing)
        ms = ''
        for field_missing in fields_missing:
            if len(ms) < 2:
                ms = field_missing
            else:
                ms = ms + ', ' + field_missing
        error_mess.append(("<div> Fields Missing :{}</div>".format(ms)))
        ms = ''
        for field_plus in fields_plus:
            if len(ms) < 2:
                ms = field_plus
            else:
                ms = ms + ', ' + field_plus
        error_mess.append(("<div> Fields PLUS :{}</div>".format(ms)))

        if len(fields_missing) == 0:
            summary.append(("<div> Header is ok </div>"))
        else:
            error.append(False)
            error_mess.append(("<div> Header is not Ok </div>"))
        _logger.warning('CHECCCC')

        if self.check:
            for index, row in enumerate(reader):
                if len(row) != number_col:
                    error.append(False)
                    error_mess.append(
                    ("<div> Row {} does not have the number of columns equal to the table header </div>".format(index)))

        dict_type = {}
        if self.check:
            for field in self.dict_import_id.field_ids.field_import_id:
                dict_type[field.name] = field.ttype

            _logger.warning(dict_type)
            for index, row in enumerate(reader):
                dict_read = {key: (value) for key, value in
                         zip(self.dict_import_id.field_ids.field_import_id.mapped('name'), row[0:])
                         }
                for key in list(dict_read.keys()):
                    if dict_type[key] == 'integer':
                        try:
                            _logger.warning(key)
                            _logger.warning('int')
                            a = int(dict_read[key])
                        except:
                            error_mess.append("<div>Wrong value a integer in {} for {}</div>".format(index, key))
                            error.append(False)
                    if dict_type[key] == 'float' or dict_type[key] == 'monetary':
                        try:
                            a = float(dict_read[key])
                        except:
                            error_mess.append("<div>Wrong value a float  in {} for {}</div>".format(index, key))
                            error.append(False)
                    if dict_type[key] == 'date':
                        try:
                            a = datetime.strptime(dict_read[key], "%Y-%m-%d").date()
                        except:
                            error_mess.append("<div>Wrong value a date in {} for {}</div>".format(index, key))
                            error.append(False)
        _logger.warning(error)
        _logger.warning(error_mess)
        if all(error) is not True:
            _logger.warning("111")
            summary.append(("<div> Check import data fails, it is a {} error</div>".format(len(error) - 1)))
            summary = summary + error_mess
            self.write({'details': '\n'.join(summary)})

            return False
        else:
            _logger.warning("222")
            summary.append(("<div> Check import data pass</div>"))
            self.write({'details': "\n".join(summary)})
            return True

    def import_model(self):
        _logger.warning(self.check)
        if self.dict_import_id:
            if self.check_data():
                self.import_generic_models()
            else :
                view_id = self.env.ref(
                    'import_data.view_import_data_form').id
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Import data '),
                    'view_mode': 'form',
                    'res_model': 'import.data',
                    'target': 'current',
                    'res_id': self.id,
                    'views': [[view_id, 'form']],

                }


        else:
            raise UserError(_("Select a model for import."))

        # if not self.check:
        #     if self.file_import == "partner":
        #         # self.update_partner_lang()
        #         self.import_generic_models(
        #             "partner.csv", header_partner_g, None, header_partner_d
        #         )
        #     # self.update_generic_models('partner.csv', 'name', header_partner_g)
        #     elif self.file_import == "cat_product":
        #         # self.export_generic_models('cat_exp.csv', header_product_cat)
        #         self.import_generic_models("categorii_produse.csv", header_product_cat)
        #     elif self.file_import == "account":
        #         self.import_generic_models(
        #             "account_account.csv", header_account_account_g
        #         )
        #         # self.import_generic_models(
        #         #    file_name="account.csv",
        #         #    header_generic=header_account_g,
        #         #    level_multiline=1,
        #         #    level_creation_allowed=1,
        #         # )
        #     elif self.file_import == "product":
        #         self.import_generic_models("produse.csv", header_product_g)
        #     # self.change_cat()
        #     # self.update_generic_models(
        #     #    "product_update.csv", "default_code", header_product_cost_g
        #     # )
        #     # self.export_generic_models('produse.csv',header_product_g)
        #     # self.update_product_models('produse.csv','name',header_product_g)
        #     # self.update_product_evinox_models('product1.csv',header_product_g)
        #     # self.update_product_correct()
        #     elif self.file_import == "inventory":
        #         # self.fix_quant()
        #         self.import_generic_models(
        #             file_name="inventar.csv",
        #             header_generic=header_inventory_g,
        #             level_creation_allowed=1,
        #         )
        #         # self.update_moveline_data()
        #         # self.delete_move_line()
        #     elif self.file_import == "bom":
        #         # self.import_generic_models('bom_line.csv', header_bom_line_g)
        #         self.manufacturing_done()
        #     elif self.file_import == "balance_partner":
        #         self.import_generic_models(
        #             "account_move_partner_one.csv",
        #             header_move_line_g,
        #             level_multiline=1,
        #             level_creation_allowed=1,
        #         )
        #     elif self.file_import == "asset":
        #         self.import_generic_models("asset.csv", header_asset_g)
        #     elif self.file_import == "valuation":
        #         # self.import_generic_models('valuation_obj.csv', header_stock_valuation_layer_g,None,header_stock_valuation_layer_d)
        #         self.update_valuation_models_multi_line(
        #             "valuation_dec.csv", header_stock_valuation_layer_g
        #         )
        #         # self.update_valution_models_fifo()
        #         # self.update_valuation_models_lot('valuation.csv')
        #         # quants = self.env['stock.quant'].sudo().search([])
        #         # quants._compute_value()
        #         # self.update_valuation_multi_account()
        #     elif self.file_import == "lot":
        #         self.import_generic_models("lot.csv", header_lot_g)
        #     elif self.file_import == "delete":
        #         self.delete_move_line()
        # else:
        #
        #     if self.file_import == "inventory":
        #         _logger.warning("Mark1")
        #         self.check_id_link("inventory.csv", header_inventory_g)

    def export_model(self):

        data = self.export_generic_models("partner.csv")
        exp_class = self.env['export.csv.file']
        exp = exp_class.create({'data_import_id': self.id})
        return exp.export_csv_data(data)

        # if self.file_import == "partner":
        #     self.export_generic_models("partner.csv", header_partner_g)
        # elif self.file_import == "cat_product":
        #     self.export_generic_models("cat_exp1.csv", header_product_cat)
        # elif self.file_import == "account":
        #     pass
        # elif self.file_import == "product":
        #     self.export_generic_models("produse.csv", header_product_g)
        # elif self.file_import == "inventory":
        #     self.export_generic_models("inventory_exp.csv", header_inventory_g)
        # elif self.file_import == "bom":
        #     self.export_generic_models("boom_exp.csv", header_bom_line_g)
        # elif self.file_import == "balance_partner":
        #     pass
        # elif self.file_import == "asset":
        #     pass
        # elif self.file_import == "valuation":
        #     pass

    def prepare_csv_file_header_and_delimiter(self):
        """ This method is used to prepare a csv file header and delimiter.

        """
        delimiter = ","
        header_generic = self.dict_import_id.get_dict()
        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        field_names = [val[0] for val in header_generic.values()]

        return delimiter, field_names

    def get_field_merge_export(self, model_level, model, level):
        ir_model_obj = self.env["ir.model.fields"]
        _logger.warning("Model relation")
        _logger.warning(model_level)
        _logger.warning(level)
        model_parent = model_level[level][0]
        _logger.warning("Model relation")
        _logger.warning(model_parent)
        field_merge = None
        if model_level[level - 1]:
            model = model_level[level - 1][0]
            field_merge = ir_model_obj.search(
                [("model", "=", model_parent), ("relation", "=", model)], limit=1
            )
        if field_merge:
            _logger.warning(field_merge.name)
            return field_merge.name
        else:
            return None

    def corect_date(self):
        inventoris = self.env["stock.inventory"].search([("state", "=", "done")])
        for inv in inventoris:
            res = {"date": "2021-06-30"}
            inv.sudo().write(res)
        return True

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
        _logger.warning("Models 0")
        _logger.warning(models)
        models_uniq = []
        for x in models:
            if x not in models_uniq:
                models_uniq.append(x)
        models = models_uniq
        model_nonnul = [model for model in models if model is not None]
        ir_model_obj = self.env["ir.model.fields"]
        _logger.warning(model_nonnul)
        if len(model_nonnul) == 1:
            model_rel = [[], [model_nonnul[0]], []]
        elif len(model_nonnul) == 2:

            field_rel = ir_model_obj.search([("model", "=", models[0]), ("relation", "=", models[1])], limit=1)
            field_rel_inv = ir_model_obj.search([("model", "=", models[1]), ("relation", "=", models[0])], limit=1)
            _logger.warning(field_rel.ttype)
            _logger.warning(field_rel_inv.ttype)
            if field_rel.ttype == 'one2many':
                model_rel = [[models[0]], [models[1]], []]
            elif field_rel.ttype == 'many2one':
                model_rel = [[models[1]], [models[0]], []]
        elif len(model_nonnul) == 3:
            dict_model_order = {}
            for model in models:
                for model_rel in models:
                    if model_rel != model:
                        dict_model_order[model] = None
                        field_rel = ir_model_obj.search([("model", "=", model), ("relation", "=", model_rel)],
                                                        limit=1)
                        if field_rel:
                            if field_rel.ttype == 'many2one':
                                dict_model_order[model] = model_rel

            for model, model_val in dict_model_order.items():
                if model_val is None:
                    val2 = [key for key, value in dict_model_order.items() if value == model]

                    val1 = [key for key, value in dict_model_order.items() if value == val2]
                model_rel = [val1, val2, model_rel]

        return model_rel

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

        _logger.warning(model_rel)

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
            self,

            level_multiline=None,
            default_model=None,
            level_creation_allowed=2,
    ):

        header_generic = self.dict_import_id.get_dict()
        default_model = self.dict_import_id.get_dict_default()
        file_name = self.dict_import_id.file_name_import_default
        level_multiline = self.dict_import_id.level_multiline
        level_creation_allowed = self.dict_import_id.level_creation_allowed
        _logger.warning("XXXXXXXX")

        _logger.warning(header_generic)

        headear_inv = self.inverse_dict1(self.dict_import_id.get_dict())
        details = []
        models = []
        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        model_level = self.dict_import_id.order_models()
        _logger.warning(model_level)
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
        if self.attachment_ids:
            data_file = self.import_file()
            csv_data = base64.b64decode(data_file.datas)
            data_file = StringIO(csv_data.decode("utf-8"))

            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)

            headers = file_reader[0]
            reader = file_reader[1:]
        else:
            if file_name:
                file_reader = []
                with open(self.get_path(file_name), "r") as infile:
                    reader = csv.reader(infile)
                    headers = next(reader)[0:]
                    for row in reader:
                        file_reader.append(row)
                        reader = file_reader

        if 1 == 1:

            _logger.warning(headear_inv)
            _logger.warning(headers)
            headers_translate = [headear_inv[h] for h in headers]

            _logger.warning("Mark1")
            _logger.warning(headers)
            _logger.warning(file_reader)
            _logger.warning(headear_inv)
            _logger.warning(headers_translate)
            _logger.warning(keys_models)
            item_dict = {}
            # _logger.warning(f"numarul de randuri{len(list(reader))}")
            for row in reader:
                _logger.warning("Mark2")
                _logger.warning(row)
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
                                                    cm, rel_keys
                                                )
                                            _logger.warning(item_object)
                                            _logger.warning(f"Merge {keyss}")
                                        if ir_model_field.ttype == "many2one":
                                            dict_filter_1[keyss] = item_object.id
                                        elif ir_model_field.ttype == "many2many":
                                            dict_filter_1[keyss] = [(4, item_object.id)]
                                            _logger.warning(item_object.name)
                                            _logger.warning(item_object.id)
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
                                    _logger.warning(dkeys)
                                    ir_model_field = ir_model_obj.search(
                                        [
                                            ("model", "=", "res.company"),
                                            ("name", "=", dkeys),
                                        ],
                                        limit=1,
                                    )
                                    if default_model[dkeys][1] == model:
                                        if dkeys in dict_filter_1.keys():
                                            if not dict_filter_1[dkeys]:
                                                dict_filter_1[dkeys] = default_model[
                                                    dkeys
                                                ][0]
                                        else:
                                            if ir_model_field.ttype != "many2one":
                                                dict_filter_1[dkeys] = default_model[
                                                    dkeys
                                                ][0]
                                            else:
                                                company = self.env[
                                                    "res.company"
                                                ].search(
                                                    [
                                                        (
                                                            "id",
                                                            "=",
                                                            default_model[dkeys][0],
                                                        )
                                                    ],
                                                    limit=1,
                                                )
                                                _logger.warning(company)
                                                dict_filter_1[dkeys] = company.id

                            # _logger.warning(dict_filter_1.keys())
                            # _logger.warning(header_default.keys())
                            # dict_filter_1.update(header_default[model])
                            _logger.warning("Mark5")
                            _logger.warning(level_multiline)

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
                                    _logger.warning("ASSASASASA")
                                    _logger.warning(domain)
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

                                if item_search and level < level_creation_allowed:
                                    item_dict[model] = item_search
                                    _logger.warning(
                                        f" FFFFFind {model}:{item_search} don`t create new item"
                                    )
                                else:
                                    if level != level_multiline:
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
                if extra_string:
                    value_search = extra_string + dict_read[field_search]
                else:
                    value_search = dict_read[field_search]
                field_update = self.env[models[0]].search(
                    [(field_search, "=", value_search)]
                )
                _logger.warning(field_update[0].name)
                dict_filter_1 = {
                    k: dict_read[k] for k in keys_models[0] if k in dict_read
                }
                _logger.warning(dict_filter_1)
                for keyss, values in header_generic.items():
                    t, m, cm, f = values
                    if keyss in keys_models[0] and keyss == "standard_price":
                        if cm:
                            _logger.warning(cm)
                            rel_keys = []
                            _logger.warning(f)
                            for ritems in f:
                                rkeys, rvalue = ritems

                                if rvalue == None:

                                    rvalue = dict_filter_1[keyss]
                                    rel_keys.append((rkeys, rvalue))
                                else:
                                    if rvalue in dict_filter_1.keys():

                                        rel_keys.append((rkeys, dict_filter_1[rvalue]))
                                    else:
                                        rel_keys.append((rkeys, rvalue))
                            item_object, mess = self.merge_models(cm, rel_keys)
                            dict_filter_1[keyss] = item_object.id
                _logger.warning(dict_filter_1)
                field_update.write({"standard_price": dict_filter_1["standard_price"]})

        return True

    def update_valution_models_fifo(self):

        items_update = self.env["stock.valuation.layer"].search([])
        for item in items_update:
            if item.description:

                if item.description[0:3] == "INV":
                    _logger.warning(item.description)
                    _logger.warning(item.remaining_qty)
                    res = {"remaining_value": item.remaining_qty * item.unit_cost}
                    _logger.warning(res["remaining_value"])
                    item.write(res)
        return True

    def delete_move_line(self):
        move_lines = self.env["stock.move.line"].search([])
        moveLine_count = []
        move_nodelete = []
        for line in move_lines:
            if line.picking_id.id:
                move_nodelete.append(line.move_id)
            else:
                _logger.warning(line.id)
                moveLine_count.append(line.id)
                line.write({"qty_done": 0, "lot_id": None})

        quants = self.env["stock.quant"].search([])
        i = 0
        for quant in quants:
            quant.sudo().unlink()
            i += 1
        _logger.warning(i)
        products = self.env["product.template"].search([])
        for product in products:
            product.write({"standard_price": 0, "tracking": "lot"})

        valuations = self.env["stock.valuation.layer"].search([])
        for val in valuations:
            val.sudo().unlink()

        account_move = self.env["account.move"].search([])

        for acc_move in account_move:
            if acc_move.journal_id.id == 6:
                _logger.warning(acc_move.state)
                acc_move.write({"state": "cancel"})

        return True

    def update_valuation_models(
            self,
            file_name,
            field_search="description",
            header_generic=header_stock_valuation_layer_g,
    ):

        mod, relmod, ks, name_inventory_list = header_inventory_g["inventory_id"]
        name_inventory = name_inventory_list[0][1]

        extra_string = f"INV:{name_inventory} - "

        headear_val_inv = self.inverse_dict1(header_stock_valuation_layer_g)

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

        with open(self.get_path(file_name), "r") as infile:
            reader = csv.reader(infile)
            headers = next(reader)[0:]
            _logger.warning(headers)
            headers_translate = [headear_val_inv[h] for h in headers]
            _logger.warning(headers_translate)
            _logger.warning(keys_models)
            for row in reader:
                dict_read = {
                    key: (value) for key, value in zip(headers_translate, row[0:])
                }
                product_name = self.env["product.template"].search(
                    [("name", "=", dict_read["product_id"])], limit=1
                )

                value_search = extra_string + product_name.name
                _logger.warning(value_search)
                row_update = self.env[models[0]].search(
                    [("description", "=", value_search)]
                )
                _logger.warning(row_update)
                res = {
                    "unit_cost": dict_read["unit_cost"],
                    "value": float(dict_read["unit_cost"])
                             * float(dict_read["quantity"]),
                    "remaining_qty": float(dict_read["quantity"]),
                    "remaining_value": float(dict_read["unit_cost"])
                                       * float(dict_read["quantity"]),
                }
                row_update.write(res)

        return True

    def update_valuation_models_lot(
            self,
            file_name,
            field_search="description",
            header_generic=header_stock_valuation_layer_g,
    ):

        mod, relmod, ks, name_inventory_list = header_inventory_g["inventory_id"]
        name_inventory = name_inventory_list[0][1]

        extra_string = f"INV:{name_inventory} - "

        headear_val_inv = self.inverse_dict1(header_stock_valuation_layer_g)

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
        with open(self.get_path(file_name), "r") as infile:
            reader = csv.reader(infile)
            headers = next(reader)[0:]
            _logger.warning(headers)
            headers_translate = [headear_val_inv[h] for h in headers]
            _logger.warning(headers_translate)
            _logger.warning(keys_models)
            for row in reader:
                dict_read = {
                    key: (value) for key, value in zip(headers_translate, row[0:])
                }
                dict_read["product_id"]
                lot = self.env["stock.production.lot"].search(
                    [("name", "=", dict_read["lot"])], limit=1
                )
                move_line = self.env["stock.move.line"].search(
                    [("lot_id", "=", lot.id)]
                )
                move_line2 = move_line[0]
                move = self.env["stock.move"].search(
                    [("id", "=", move_line2.move_id.id)]
                )
                valuation_update = self.env["stock.valuation.layer"].search(
                    [("stock_move_id", "=", move.id)], limit=1
                )
                move.write({"date": dict_read["vechime_stoc"]})
                move_line.write({"date": dict_read["vechime_stoc"]})
                lot.sudo().write({"create_date": dict_read["vechime_stoc"]})

                res = {
                    "unit_cost": dict_read["unit_cost"],
                    "value": float(dict_read["unit_cost"])
                             * float(dict_read["quantity"]),
                    "remaining_qty": valuation_update["quantity"],
                    "remaining_value": float(dict_read["unit_cost"])
                                       * float(dict_read["quantity"]),
                    "date": dict_read["vechime_stoc"],
                }
                _logger.warning(lot.product_id.name)
                if valuation_update["quantity"] - float(dict_read["quantity"]) > 0.01:
                    _logger.warning(valuation_update.description)
                    _logger.warning(lot.product_id.name)
                    _logger.warning(move_line.qty_done)
                    _logger.warning(dict_read["quantity"])
                    _logger.warning(valuation_update["quantity"])
                    _logger.warning(valuation_update["remaining_qty"])
                    _logger.warning(valuation_update["remaining_value"])
                    _logger.warning(valuation_update["value"])
                    _logger.warning(move["date"])

                valuation_update.write(res)

            #     if prod_id  in dict_file_product.keys():
            #          dict_file_product[prod_id].append((dict_read['unit_cost'],dict_read['quantity']))
            #     else:
            #         dict_file_product[prod_id]= [(dict_read['unit_cost'],dict_read['quantity'])]
            # for product_code in dict_file_product.keys():
            #     new_dict = {}
            #     product_name = self.env['product.template'].search([('default_code', '=', product_code)], limit=1)
            #     value_search = extra_string + product_name.name
            #     for item in  dict_file_product[product_code]:
            #         unit_cost, quantity = item
            #         quantity_str = str(quantity)
            #         if quantity_str in new_dict.keys():
            #             new_dict[quantity_str].append(unit_cost)
            #         else:
            #             new_dict[quantity_str]=[unit_cost]
            #         for quantity in new_dict.keys():
            #
            #             rows_update = self.env[models[0]].search([('description', '=', value_search),('quantity','=',quantity)])
            #             list_rows_update =[item for item in rows_update]
            #             if len(new_dict[quantity_str])!=len(list_rows_update):
            #
            #                 _logger.warning(value_search)
            #                 _logger.warning(quantity)
            #                 _logger.warning(rows_update)
            #                 _logger.warning(len(new_dict[quantity_str]))
            #                 i=0
            #                 # for item_valuation in rows_update:
            #                 #     _logger.warning(i)
            #                 #     _logger.warning(new_dict[quantity][i])
            #                 #     i+=1
            #     # res = {'unit_cost': dict_read['unit_cost'],
            #     #        'value': float(dict_read['unit_cost']) * float(dict_read['quantity'])}
            #     # row_update.write(res)
        return True

    def update_valuation_models_multi_line(self, file_name, header_generic):

        mod, relmod, ks, name_inventory_list = header_inventory_g["inventory_id"]
        name_inventory = name_inventory_list[0][1]
        extra_string = f"INV:{name_inventory}"
        headear_val_inv = self.inverse_dict1(header_stock_valuation_layer_g)

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
        valuation_model = self.env["stock.valuation.layer"]

        _logger.warning(keys_models)
        List_special = []
        with open(self.get_path(file_name), "r") as infile:
            reader = csv.reader(infile)
            headers = next(reader)[0:]
            _logger.warning(headers)
            headers_translate = [headear_val_inv[h] for h in headers]
            _logger.warning("capul vvvv ")
            _logger.warning(headers_translate)
            _logger.warning(keys_models)
            for row in reader:
                dict_read = {
                    key: (value) for key, value in zip(headers_translate, row[0:])
                }
                _logger.warning("Dictionatul citit vv")
                _logger.warning(dict_read)
                product = self.env["product.product"].search(
                    [("default_code", "=", dict_read["product_id"])], limit=1
                )
                account_id = product.categ_id.property_stock_valuation_account_id
                if not account_id:
                    List_special.append(dict_read["product_id"])
                _logger.warning("Accountt ttt")
                _logger.warning(account_id)
                name_depozit = dict_read["depozit"]
                _logger.warning(name_depozit)
                location = self.env["stock.location"].search(
                    [("complete_name", "=", name_depozit)]
                )
                _logger.warning(location)
                move_inventory = self.env["stock.move"].search(
                    [
                        ("reference", "=", extra_string),
                        ("product_id", "=", product.id),
                        ("location_dest_id", "=", location.id),
                    ]
                )

                _logger.warning(extra_string)
                _logger.warning(product.id)
                _logger.warning(location.id)
                _logger.warning(move_inventory)

                res = {
                    "company_id": self.env.company.id,
                    "product_id": product.id,
                    "quantity": float(dict_read["quantity"]),
                    "unit_cost": dict_read["unit_cost"],
                    "value": float(dict_read["unit_cost"])
                             * float(dict_read["quantity"]),
                    "remaining_qty": float(dict_read["quantity"]),
                    "remaining_value": float(dict_read["unit_cost"])
                                       * float(dict_read["quantity"]),
                    "date": dict_read["vechime_stoc"],
                    "account_id": account_id.id if account_id else None,
                    "stock_move_id": move_inventory.id,
                }
                valuation_model.create(res)
        _logger.warning(List_special)
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
        model_level = self.dict_import_id.order_models()

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
                                                    cm, rel_keys, check=True
                                                )
                                                if mess:
                                                    string_details += f"<div>In Row Number {number_row}</div>"
                                                    string_details += mess
                                                    list_fail.append(mess)

                number_row += 1
        self.details = str(string_details)
        _logger.warning(list_fail[0])
        return True

    def update_product_models(
            self, file_name, field_search, header_generic, extra_string=None
    ):
        self.inverse_dict1(header_generic)

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
        products_update = self.env["product.template"].search([])
        for prod in products_update:
            prod.write({"type": "product"})

        # with open(self.get_path(file_name), "r") as infile:
        #     reader = csv.reader(infile)
        #     headers = next(reader)[0:]
        #     _logger.warning(headers)
        #     headers_translate = [headear_partener_inv[h] for h in headers]
        #     _logger.warning(headers_translate)
        #     _logger.warning(keys_models)
        #     for row in reader:
        #         dict_read = {key: (value) for key, value in zip(headers_translate, row[0:])}
        #         value_search = dict_read[field_search]
        #         field_update = self.env[models[0]].search([(field_search, '=', value_search)])
        #         dict_filter_1 = dict((k, dict_read[k]) for k in keys_models[0] if k in dict_read)
        #         _logger.warning(dict_filter_1)
        #         _logger.warning(value_search)
        #         if field_update['taxes_id']:
        #             _logger.warning('yep')
        #             _logger.warning(field_update['taxes_id'])
        #             tax_find = field_update['taxes_id']
        #             field_update.write({'taxes_id': [(3, tax_find.id)]})
        #             _logger.warning(field_update['taxes_id'])
        #
        #         if field_update['supplier_taxes_id']:
        #             _logger.warning('yyep')
        #             _logger.warning(field_update['supplier_taxes_id'])
        #             tax_find = field_update['supplier_taxes_id']
        #             field_update.write({'taxes_id': [(3, tax_find.id)]})
        #             _logger.warning(field_update['supplier_taxes_id'])
        #
        #         rvalue = dict_filter_1['taxes_id']
        #         rel_keys = [('name', rvalue)]
        #
        #         item_object, mess = self.merge_models('account.tax', dict_filter_1['taxes_id'], rel_keys)
        #         dict_filter_1['taxes_id'] = [(4, item_object.id)]
        #
        #         rvalue = dict_filter_1['supplier_taxes_id']
        #         rel_keys = [('name', rvalue)]
        #         item_object, mess = self.merge_models('account.tax', dict_filter_1['supplier_taxes_id'], rel_keys)
        #         dict_filter_1['supplier_taxes_id'] = [(4, item_object.id)]
        #
        #         _logger.warning('Final')
        #         _logger.warning(dict_filter_1)
        #         field_update.write({'taxes_id': dict_filter_1['taxes_id'],
        #                             'supplier_taxes_id': dict_filter_1['supplier_taxes_id'],
        #                            })
        # if
        #     t, m, cm, f = values
        #     if keyss in keys_models[0]:
        #         if cm:
        #             _logger.warning(cm)
        #             item_object = self.merge_models(cm, dict_filter_1[keyss], f)
        #             dict_filter_1[keyss] = item_object.id
        # field_update.write(dict_filter_1)

        return True

    def export_generic_models(self, file_name):

        if file_name is None:
            file_name = self.dict_import_id.file_name_export_default

        header_generic = self.dict_import_id.get_dict()

        model_level = self.dict_import_id.order_models()

        if len(model_level[2]) > 0:
            model_write = model_level[2][0]
            level_write = 2
            field_merge = self.get_field_merge_export(model_level, model_write, 2)
        else:
            if len(model_level[1]) > 0:
                model_write = model_level[1][0]
                level_write = 1
                field_merge = self.get_field_merge_export(model_level, model_write, 1)
            else:
                model_write = model_level[0][0]
                level_write = 0
        _logger.warning("Export")
        _logger.warning(model_level)
        _logger.warning(model_write)
        _logger.warning(level_write)
        _logger.warning(field_merge)
        all_row = []

        model_write_obj = self.env['ir.model'].search([('model', '=', model_write)])
        if len(model_level[0]) > 0:
            model_level_sup = model_level[0][0]
            model_level_sup_obj = self.env['ir.model'].search([('model', '=', model_level_sup)])
            fields_model_sup = self.dict_import_id.field_ids.filtered(
                lambda l: l.model_import_id == model_level_sup_obj)

        values_write = self.env[model_write].search([])

        fields_model_write = self.dict_import_id.field_ids.filtered(lambda l: l.model_import_id == model_write_obj)

        for item_write in values_write:
            dict = {}
            for field in fields_model_write:
                _logger.warning(field)
                _logger.warning(item_write)
                if field.comodel_import_id.model == False:
                    res = getattr(item_write, field.field_import_id.name, None)
                    type = field.field_import_id.ttype
                else:
                    obj_rel = getattr(item_write, field.field_import_id.name)
                    _logger.warning(obj_rel)
                    if field.field_import_id.ttype != 'many2many':

                        type = field.field1_comodel_id.ttype
                        res = getattr(obj_rel, field.field1_comodel_id.name, None)
                    else:
                        type = field.field1_comodel_id.ttype
                        for obj_relitem in obj_rel[:1]:
                            res = getattr(obj_relitem, field.field1_comodel_id.name, None)

                dict[field.name_field_file] = correct_value(res, type)
            if field_merge:
                rel_id = getattr(item_write, field_merge)
                _logger.warning(item_write)
                _logger.warning(rel_id)
                values_write_sup = rel_id
                for field_sup in fields_model_sup:
                    if field_sup.comodel_import_id.model == False:
                        res = getattr(values_write_sup[0], field_sup.field_import_id.name, None)
                        type = field_sup.field_import_id.ttype
                    else:
                        obj_rel = getattr(values_write_sup[0], field_sup.field_import_id.name)
                        res = getattr(obj_rel, field_sup.field1_comodel_id.name, None)
                        type = field_sup.field1_comodel_id.ttype
                    dict[field_sup.name_field_file] = correct_value(res, type)
            all_row.append(dict)

        return all_row

    def export_generic_models_old(self, file_name, header_generic):

        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        model_level = self.dict_import_id.order_models()

        _logger.warning(model_level)
        if len(model_level[2]) > 0:
            model_write = model_level[2][0]
            level_write = 2
            field_merge = self.get_field_merge_export(model_level, model_write, 2)

        else:
            if len(model_level[1]) > 0:
                model_write = model_level[1][0]
                level_write = 1
                field_merge = self.get_field_merge_export(model_level, model_write, 1)
            else:
                model_write = model_level[0][0]
                level_write = 0

        values_write = self.env[model_write].search([])
        with open(self.get_path(file_name), mode="w") as csv_file:
            fieldnames = [val[0] for val in header_generic.values()]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            self.env[model_write]
            # models_ids = self.env['product.template'].search([('id', '=', rule.product_id.id)])
            # for val in values_write:
            #     new_dict = val.read(list(set(model_obj._fields)))
            #     _logger.warning(new_dict)
            new_dict = {}
            ir_model_obj = self.env["ir.model.fields"]

            model_write_field = ir_model_obj.search([("model", "=", model_write)])
            _logger.warning(model_write_field)
            for val in values_write:
                for field in model_write_field:
                    if 1 == 1:
                        if field.ttype not in ["many2one", "many2many", "one2many"]:
                            if field.name in dir(val):
                                _logger.warning(field.name)
                                _logger.warning(val[field.name])
                                _logger.warning(field.ttype)
                                if (
                                        val[field.name] == False
                                        and field.ttype != "boolean"
                                ):
                                    new_dict[field.name] = ""
                                else:
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
                                        if val_rel_found[name_field_rel] == False:
                                            new_dict[field.name] = ""
                                        else:
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
                if level_write == 2:
                    val_merge_id = val[field_merge]
                    _logger.warning(val_merge_id)
                    _logger.warning(model_level[1][0])
                    # dict_parent= self.env(model_level[1][0]).search([('id','=',val_merge_id.id)])
                elif level_write == 1:
                    val_merge_id = val[field_merge]
                    # dict_parent = self.env(model_level[0][0]).search([('id', '=', val_merge_id.id)])

                nnew_dict = {}
                for keyy in header_generic.keys():
                    key_model = self.translate_double_key(keyy)
                    if (
                            header_generic[keyy] != 0
                            and header_generic[keyy][1] == model_write
                    ):
                        nnew_dict[header_generic[keyy][0]] = new_dict[key_model]
                    if (
                            level_write == 2
                            and [keyy] != 0
                            and header_generic[keyy][1] == model_level[1][0]
                    ):
                        parent_model_write_field = ir_model_obj.search(
                            [
                                ("model", "=", model_level[1][0]),
                                ("name", "=", key_model),
                            ]
                        )
                        _logger.warning(parent_model_write_field.name)
                        _logger.warning(parent_model_write_field.ttype)
                        if parent_model_write_field.ttype in ["many2one"]:
                            t, m, cm, f = header_generic[keyy]
                            name_field_rel, val_rel = f[0]
                            val_rel_found = self.env[cm].search(
                                [("id", "=", val_merge_id[key_model].id)]
                            )
                            if parent_model_write_field.ttype == "many2one":
                                _logger.warning(val_rel_found[name_field_rel])
                                _logger.warning(field.name)
                                if val_rel_found[name_field_rel] == False:
                                    nnew_dict[header_generic[keyy][0]] = ""
                                else:
                                    nnew_dict[header_generic[keyy][0]] = val_rel_found[
                                        name_field_rel
                                    ]
                        else:
                            _logger.warning(val_merge_id[key_model])
                            nnew_dict[header_generic[keyy][0]] = val_merge_id[key_model]
                    if (
                            level_write == 1
                            and [keyy] != 0
                            and header_generic[keyy][1] == model_level[0][0]
                    ):
                        parent_model_write_field = ir_model_obj.search(
                            [
                                ("model", "=", model_level[0][0]),
                                ("name", "=", key_model),
                            ]
                        )
                        _logger.warning(parent_model_write_field.name)
                        _logger.warning(parent_model_write_field.ttype)
                        if parent_model_write_field.ttype in ["many2one"]:
                            t, m, cm, f = header_generic[keyy]
                            name_field_rel, val_rel = f[0]
                            val_rel_found = self.env[cm].search(
                                [("id", "=", val_merge_id[key_model].id)]
                            )
                            if parent_model_write_field.ttype == "many2one":
                                _logger.warning(val_rel_found[name_field_rel])
                                _logger.warning(field.name)
                                if val_rel_found[name_field_rel] == False:
                                    nnew_dict[header_generic[keyy][0]] = ""
                                else:
                                    nnew_dict[header_generic[keyy][0]] = val_rel_found[
                                        name_field_rel
                                    ]
                        else:
                            nnew_dict[header_generic[keyy][0]] = val_merge_id[key_model]
                writer.writerow(nnew_dict)
        csv_file.close()

    # def serarch_id_model (self,header_generic,model_level,key_model,keyy):
    #     ir_model_obj =self.env['ir.model.fields']
    #     parent_model_write_field = ir_model_obj.search([('model', '=', model_level[1][0]), ('name', '=', key_model)])
    #     _logger.warning(parent_model_write_field.name)
    #     _logger.warning(parent_model_write_field.ttype)
    #     if parent_model_write_field.ttype in ['many2one']:
    #         t, m, cm, f = header_generic[keyy]
    #         name_field_rel, val_rel = f[0]
    #         val_rel_found = self.env[cm].search([('id', '=', val_merge_id[key_model].id)])
    #         if parent_model_write_field.ttype == 'many2one':
    #             _logger.warning(val_rel_found[name_field_rel])
    #             _logger.warning(field.name)
    #             if val_rel_found[name_field_rel] == False:
    #                 nnew_dict[header_generic[keyy][0]] = ''
    #             else:
    #                 nnew_dict[header_generic[keyy][0]] = val_rel_found[name_field_rel]

    def update_product_evinox_models(self, file_name, header_generic):
        # update in product.template product
        headear_val_inv = self.inverse_dict1(header_generic)
        models = []
        file_csv = []
        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        for keyss, values in header_generic.items():
            if values != 0:
                t, m, cm, f = values
                _logger.warning(f"Model {m}")
                models.append(m)
        models = list(set(models))

        keys_models = []
        for model in models:
            keys_model = []
            for keyss, values in header_generic.items():
                t, m, cm, f = values
                if m == model:
                    keys_model.append(keyss)
            keys_models.append(keys_model)

        _logger.warning(keys_models)
        with open(self.get_path(file_name), "r") as infile:
            reader = csv.reader(infile)
            headers = next(reader)[0:]
            headers_translate = [headear_val_inv[h] for h in headers]
            model_level = self.dict_import_id.order_models()
            _logger.warning(headers_translate)
            _logger.warning(keys_models)
            for row in reader:
                dict_read = {
                    key: (value) for key, value in zip(headers_translate, row[0:])
                }
                value_search = dict_read["code_uk"]
                _logger.warning(value_search)
                row_update = self.env["product.template"].search(
                    [("default_code", "=", value_search)], limit=1
                )
                if len(row_update) == 1:

                    _logger.warning(f"Find code {row_update.name}")
                    res = {
                        "default_code": dict_read["default_code"],
                        "code_uk": dict_read["code_uk"],
                        "description": dict_read["description"],
                        "up_product": "Done",
                    }

                    keyss = "categ_id"

                    # Merge link id model
                    ir_model_obj = self.env["ir.model.fields"]
                    ir_model_field = ir_model_obj.search(
                        [("model", "=", "product.category"), ("name", "=", keyss)],
                        limit=1,
                    )
                    _logger.warning(f"{keyss}:{ir_model_field.ttype}")
                    f = "name", None
                    rel_keys = []
                    _logger.warning(f)
                    rkeys, rvalue = f

                    rvalue = dict_read[keyss]
                    rel_keys = [(rkeys, rvalue)]
                    item_object, mess = self.merge_models("product.category", rel_keys)
                    res[keyss] = item_object.id
                    _logger.warning("CAtegoria")
                    _logger.warning(res[keyss])
                    _logger.warning(row_update)
                    if row_update.name == dict_read["name"]:
                        row_update.write(res)
                    else:
                        res["name"] = dict_read["name"]
                        _logger.warning(
                            f'Name issue {dict_read["name"]} is not {row_update.name}'
                        )
                        row_update.write(res)

                elif len(row_update) == 0:
                    value_search = dict_read["name"]
                    _logger.warning(value_search)
                    _logger.warning("MMMMark1name")
                    row_update = self.env["product.template"].search(
                        [("name", "ilike", value_search)], limit=1
                    )
                    _logger.warning(row_update)
                    if row_update:
                        _logger.warning(f"Find after Name{row_update.name}")
                        res = {
                            "default_code": dict_read["default_code"],
                            "code_uk": dict_read["code_uk"],
                            "description": dict_read["description"],
                            "up_product": "Done",
                        }
                        keyss = "categ_id"
                        f = "name", None
                        _logger.warning(f)
                        rkeys, rvalue = f
                        rvalue = dict_read[keyss]
                        rel_keys = [("name", rvalue)]
                        _logger.warning(rel_keys)
                        item_object, mess = self.merge_models(
                            "product.category", rel_keys
                        )
                        res[keyss] = item_object.id
                        _logger.warning(row_update)
                        row_update.write(res)
                    else:
                        _logger.warning("Not Found object")
                        file_csv.append(row)
            _logger.warning(file_csv)
            # with open(self.get_path('outputp.csv'), 'w', newline='') as csvfile:
            #     writer = csv.writer(csvfile)
            #     writer.writerows(file_csv)
            # for level, models in enumerate(model_level):
            #     _logger.warning('CCCreate new product')
            #     _logger.warning(models)
            #     for model in models:
            #         _logger.warning(f'an object of type{model} is created')
            #
            #         # _logger.warning(keys_models)
            #         keys_model = keys_models[model]
            #         # _logger.warning('Model keys')
            #         # _logger.warning(keys_model)
            #         # _logger.warning('Dict 0000')
            #         # se selecteaza campurile din dic_read care sunt in model
            #         dict_filter_00 = dict(
            #             (k, dict_read[k]) for k, v in header_generic.items() if
            #             v[1] == model and k in dict_read.keys())
            #
            #         # se transforma campul cu _1 ( care apare in mai multe modele) cu denumirea campului din model
            #         dict_filter_0 = dict(
            #             (self.translate_double_key(k), value) for k, value in dict_filter_00.items())
            #
            #         _logger.warning((dict_filter_0))
            #         # se verifica daca campurile sunt in model ( luat din odoo) si sa nu fie nule
            #         dict_filter_1 = dict((k, dict_filter_0[k]) for k in keys_model if
            #                              k in dict_filter_0 and dict_filter_0[k])
            #         # _logger.warning("Dict Filter")
            #         # _logger.warning(dict_filter_1)
            #         search_key = None
            #         for keyss, values in header_generic.items():
            #             t, m, cm, f = values
            #             if keyss in dict_filter_1.keys():
            #                 if cm:
            #                     # Merge link id model
            #                     ir_model_obj = self.env['ir.model.fields']
            #                     ir_model_field = ir_model_obj.search(
            #                         [('model', '=', m), ('name', '=', keyss)], limit=1)
            #                     _logger.warning(f'{keyss}:{ir_model_field.ttype}')
            #                     if ir_model_field.ttype == 'many2one' or 'many2many':
            #                         if f:
            #                             rel_keys = []
            #                             _logger.warning(f)
            #                             for ritems in f:
            #                                 rkeys, rvalue = ritems
            #
            #                                 if rvalue == None:
            #
            #                                     rvalue = dict_filter_1[keyss]
            #                                     rel_keys.append((rkeys, rvalue))
            #                                 else:
            #                                     if rvalue in dict_filter_1.keys():
            #
            #                                         rel_keys.append((rkeys, dict_filter_1[rvalue]))
            #                                     else:
            #                                         rel_keys.append((rkeys, rvalue))
            #
            #                             item_object, mess = self.merge_models(cm, dict_filter_1[keyss],
            #                                                                   rel_keys)
            #                         _logger.warning(item_object)
            #                         _logger.warning(f'Merge {keyss}')
            #                     if ir_model_field.ttype == 'many2one':
            #                         dict_filter_1[keyss] = item_object.id
            #                     elif ir_model_field.ttype == 'many2many':
            #                         dict_filter_1[keyss] = [(4, item_object.id)]
            #                         _logger.warning(item_object.name)
            #                         _logger.warning(item_object.id)
            #                 else:
            #                     if f:
            #                         search_key = keyss, f
            #         if level > 0:
            #             field_merge = self.get_field_merge(model_level, model, item_dict)
            #             _logger.warning(field_merge)
            #             dict_filter_1.update(field_merge)
            #         # insert default value
            #         _logger.warning("Mark5")
            #         dict_filter_1 = self.convert_type_field(dict_filter_1, model)
            #         _logger.warning(dict_filter_1)
            #         if 1 == 1:
            #             if search_key:
            #                 keyss, f = search_key
            #                 if 1 == 1:
            #                     rel_keys = []
            #                     _logger.warning(f)
            #                     for ritems in f:
            #                         rkeys, rvalue = ritems
            #                         _logger.warning("Initial")
            #                         _logger.warning(f'{rkeys}:{rvalue}')
            #                         if rvalue == None:
            #                             _logger.warning("Latura None, get value")
            #                             rvalue = dict_filter_1[keyss]
            #                             rel_keys.append((rkeys, rvalue))
            #                         else:
            #                             if rvalue in dict_filter_1.keys():
            #                                 rel_keys.append((rkeys, dict_filter_1[rvalue]))
            #                             else:
            #                                 rel_keys.append((rkeys, rvalue))
            #                     _logger.warning("RREl Keys")
            #                     _logger.warning(rel_keys)
            #                 domain = []
            #                 for rkeys, rvalue in rel_keys:
            #                     domain.append((rkeys, '=', rvalue))
            #
            #                 item_search = self.env[model].search(domain, limit=1)
            #
            #             else:
            #                 ir_model_obj = self.env['ir.model.fields']
            #                 ir_model_field = ir_model_obj.search([('model', '=', model)])
            #
            #                 domain = []
            #
            #                 dict_filter_str_float = []
            #                 for field in ir_model_field:
            #
            #                     if field.name in dict_filter_1.keys():
            #                         if field.ttype in ["char", "text", "integer", "float", "boolean",
            #                                            "monetary", "selection"]:
            #                             dict_filter_str_float.append(field.name)
            #
            #                 for field in dict_filter_str_float:
            #                     domain.append((field, "=", dict_filter_1[field]))
            #                 _logger.warning(domain)
            #                 item_search = self.env[model].search(domain, limit=1)
            #
            #             if item_search and level < 2:
            #                 item_dict[model] = item_search
            #                 _logger.warning(f' Find {model}:{item_search} don`t create new item')
            #             else:
            #                 item_dict[model] = self.env[model].sudo().create(dict_filter_1)
            #                 _logger.warning(f'Create new item {model} id{item_dict[model].id}')
            #
            #             _logger.warning(item_dict)

        return True

    def update_product_correct(self):
        cat_id = self.env["product.category"].search(
            [("name", "=", "Alte mat. Consumabile")]
        )
        products_consumabile = self.env["product.template"].search(
            [("categ_id", "=", cat_id.id)]
        )

        for product in products_consumabile:
            if product.default_code:
                if len(product.default_code) == 10:
                    _logger.warning(product.default_code)
                    _logger.warning(product.default_code[5])
                    if product.default_code[5] != "S":
                        prev = product.default_code[0:5]
                        last = product.default_code[5:]
                        res = prev + "S" + last
                        _logger.warning(res)
                        product.write({"default_code": res})
        return True

    def update_partner_lang(self):
        lang = self.env["res.lang"].search([("code", "=", "ro_RO")])
        partners = self.env["res.partner"].search([])
        for partner in partners:
            res = {"lang": "ro_RO"}
            partner.write(res)
        return True

    def update_moveline_data(self):
        find_date = "2021-07-26"
        findd_date = datetime.strptime(find_date, "%Y-%m-%d").date()
        _logger.warning(findd_date)
        move_line = self.env["stock.move.line"].search([])
        move = self.env["stock.move"].search([])
        quats = self.env["stock.quant"].sudo().search([])
        _logger.warning(len(move_line))
        _logger.warning(len(move))
        _logger.warning(len(quats))
        l = []
        m = []
        q = []
        for line in move_line:
            if findd_date == line.date.date():
                l.append(line)
                res = {"date": "2021-06-30"}
                line.write(res)

        for mov in move:
            if findd_date == mov.date.date():
                m.append(mov)
                res = {"date": "2021-06-30"}
                mov.write(res)

        for qut in quats:
            if findd_date == qut.in_date.date():
                q.append(qut)
                res = {"in_date": "2021-06-30"}
                qut.write(res)

        _logger.warning(len(l))
        _logger.warning(len(m))
        _logger.warning(len(q))

        return True

    def change_cat(self):
        cod_product = [
            763,
            764,
            765,
            766,
            768,
            770,
            771,
            190,
            179,
            785,
            191,
            787,
            200,
            788,
        ]
        cat_ambalaje = self.env["product.category"].search(
            [("name", "=", "Materiale de ambalat")]
        )
        cod_marfuri = [316, 317, 319, 429, 430, 431, 919, 110, 113, 534, 53]
        cat_marfuri = self.env["product.category"].search([("name", "=", "Marfuri")])
        cod_matprime = [136, 137, 45, 133]
        cat_materii_prime = self.env["product.category"].search(
            [("name", "=", "Materii prime")]
        )
        cod_ambalaj = [916]
        cat_amb_old = self.env["product.category"].search([("name", "=", "Ambalaje")])
        cat_produse_finite = self.env["product.category"].search(
            [("name", "=", "Produse Finite")]
        )
        cod_prodfinte = [302]
        _logger.warning(cat_ambalaje)
        _logger.warning(cat_ambalaje.name)
        for product_id in cod_product:
            product = self.env["product.product"].search(
                [("default_code", "=", product_id)]
            )
            _logger.warning(product.name)
            product.write({"categ_id": cat_ambalaje.id})

        for product_id in cod_marfuri:
            product = self.env["product.product"].search(
                [("default_code", "=", product_id)]
            )
            _logger.warning(product.name)
            product.write({"categ_id": cat_marfuri.id})

        for product_id in cod_matprime:
            product = self.env["product.product"].search(
                [("default_code", "=", product_id)]
            )
            _logger.warning(product.name)
            product.write({"categ_id": cat_materii_prime.id})

        for product_id in cod_ambalaj:
            product = self.env["product.product"].search(
                [("default_code", "=", product_id)]
            )
            _logger.warning(product.name)
            product.write({"categ_id": cat_amb_old.id})

        for product_id in cod_prodfinte:
            product = self.env["product.product"].search(
                [("default_code", "=", product_id)]
            )
            _logger.warning(product.name)
            product.write({"categ_id": cat_produse_finite.id})

    def update_valuation_multi_account(self):
        description = "INV:Inventar_31/08_initial - Eticheta dulceata de visine"
        quantity = 1500
        stock_val = self.env["stock.valuation.layer"].search(
            [("description", "=", description), ("quantity", "=", quantity)]
        )
        _logger.warning(stock_val)
        _logger.warning(stock_val.account_id)
        _logger.warning(stock_val.account_id.name)
        stock_val.write({"account_id": 173})
        _logger.warning(stock_val.account_id.name)

    def fix_quant(self):
        stock_quants_0 = self.env["stock.quant"].search(
            [("location_id", "=", 8), ("quantity", "<", 0)]
        )
        _logger.warning(stock_quants_0)
        for quant_0 in stock_quants_0:
            quant_0.sudo().write({"quantity": 0})
        move_line = self.env["stock.move.line"].search([("location_dest_id", "=", 32)])
        stock_quants = self.env["stock.quant"].search([("location_id", "=", 32)])
        move_line_dest = self.env["stock.move.line"].search(
            [("location_id", "=", 32), ("state", "=", "done")]
        )
        products_location = move_line.mapped("product_id")
        for product in products_location:
            move_line_product = move_line.filtered(lambda ml: ml.product_id == product)
            stock_quants_product = stock_quants.filtered(
                lambda ml: ml.product_id == product
            )
            lots_product = move_line_product.mapped("lot_id")
            move_line_nolot = move_line_product.filtered(lambda mln: mln.lot_id is None)
            _logger.warning(product.name)
            for mln in move_line_product:
                # _logger.warning(mln.lot_id)
                if not mln.lot_id:
                    _logger.warning(f"move no lot{mln.qty_done}")
                    quant_nolot = mln.qty_done
            for mlnf in move_line_dest:
                if not mlnf.lot_id:
                    quant_nolotf = mlnf.qty_done
            for sqnl in stock_quants_product:
                if not sqnl.lot_id:
                    _logger.warning(f"quant old no lot {sqnl.quantity}")
                    _logger.warning(f"move in no lot{quant_nolot}")
                    _logger.warning(f"move out no lot{quant_nolotf}")
                    sqnl.sudo().write({"quantity": quant_nolot - quant_nolotf})
            for lot in lots_product:
                move_line_lot = move_line_product.filtered(
                    lambda mlp: mlp.lot_id == lot
                )
                move_line_lot_from = move_line_dest.filtered(
                    lambda mlp: mlp.lot_id == lot
                )
                quant_lot = sum(move_line_lot.mapped("qty_done")) - sum(
                    move_line_lot_from.mapped("qty_done")
                )
                quant_lot_old = stock_quants_product.filtered(
                    lambda mlp: mlp.lot_id == lot
                )
                _logger.warning(lot.name)
                if quant_lot_old:
                    # _logger.warning(quant_lot_old.mapped('lot_id'))
                    _logger.warning(f'quant lot{quant_lot_old.mapped("quantity")}')
                    first_quant = quant_lot_old[0]
                    first_quant.sudo().write({"quantity": quant_lot})
                    for next_quant in quant_lot_old[1:]:
                        next_quant.sudo().write({"quantity": 0})
                _logger.warning(f"move lot sum {quant_lot}")

    def manufacturing_done(self):
        manufacturing_order = self.env["mrp.production"].search(
            [("state", "=", "draft")]
        )
        for order in manufacturing_order:
            form = Form(order)
            product = order.product_id
            bom = self.env["mrp.bom"].search([("product_tmpl_id", "=", product.id)])
            _logger.warning(bom)
            form.bom_id = bom
            form.save()
            order.action_confirm()
            order.action_assign()
            order.button_mark_done()

    def update_product_models(
            self, file_name, field_search, header_generic, extra_string=None
    ):
        self.inverse_dict1(header_generic)

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
        products_update = self.env["product.template"].search([])
        for prod in products_update:
            prod.write({"type": "product"})

        # with open(self.get_path(file_name), "r") as infile:
        #     reader = csv.reader(infile)
        #     headers = next(reader)[0:]
        #     _logger.warning(headers)
        #     headers_translate = [headear_partener_inv[h] for h in headers]
        #     _logger.warning(headers_translate)
        #     _logger.warning(keys_models)
        #     for row in reader:
        #         dict_read = {key: (value) for key, value in zip(headers_translate, row[0:])}
        #         value_search = dict_read[field_search]
        #         field_update = self.env[models[0]].search([(field_search, '=', value_search)])
        #         dict_filter_1 = dict((k, dict_read[k]) for k in keys_models[0] if k in dict_read)
        #         _logger.warning(dict_filter_1)
        #         _logger.warning(value_search)
        #         if field_update['taxes_id']:
        #             _logger.warning('yep')
        #             _logger.warning(field_update['taxes_id'])
        #             tax_find = field_update['taxes_id']
        #             field_update.write({'taxes_id': [(3, tax_find.id)]})
        #             _logger.warning(field_update['taxes_id'])
        #
        #         if field_update['supplier_taxes_id']:
        #             _logger.warning('yyep')
        #             _logger.warning(field_update['supplier_taxes_id'])
        #             tax_find = field_update['supplier_taxes_id']
        #             field_update.write({'taxes_id': [(3, tax_find.id)]})
        #             _logger.warning(field_update['supplier_taxes_id'])
        #
        #         rvalue = dict_filter_1['taxes_id']
        #         rel_keys = [('name', rvalue)]
        #
        #         item_object, mess = self.merge_models('account.tax', dict_filter_1['taxes_id'], rel_keys)
        #         dict_filter_1['taxes_id'] = [(4, item_object.id)]
        #
        #         rvalue = dict_filter_1['supplier_taxes_id']
        #         rel_keys = [('name', rvalue)]
        #         item_object, mess = self.merge_models('account.tax', dict_filter_1['supplier_taxes_id'], rel_keys)
        #         dict_filter_1['supplier_taxes_id'] = [(4, item_object.id)]
        #
        #         _logger.warning('Final')
        #         _logger.warning(dict_filter_1)
        #         field_update.write({'taxes_id': dict_filter_1['taxes_id'],
        #                             'supplier_taxes_id': dict_filter_1['supplier_taxes_id'],
        #                            })
        # if
        #     t, m, cm, f = values
        #     if keyss in keys_models[0]:
        #         if cm:
        #             _logger.warning(cm)
        #             item_object = self.merge_models(cm, dict_filter_1[keyss], f)
        #             dict_filter_1[keyss] = item_object.id
        # field_update.write(dict_filter_1)

        return True
