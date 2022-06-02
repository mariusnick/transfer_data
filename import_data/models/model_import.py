# Copyright 2022 OEC Romania SRL
# License OPL-1.0 or later
# (https://www.odoo.com/documentation/user/14.0/legal/licenses/licenses.html#).
import logging
import base64
import csv
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.tools.safe_eval import safe_eval, test_python_expr

from io import StringIO

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ImportDict(models.Model):
    _name = "import.dict"
    _description = "models for import"

    name = fields.Char('Name')
    level_multiline = fields.Integer('Level_multiline')
    level_creation_allowed = fields.Integer('Allowed level creation')
    field_ids = fields.One2many('import.fields', 'dict_import_id', string='Fields', copy=True)
    field_default_ids = fields.One2many('import.default.fields', 'dict_import_id', string='Default Fields', copy=True)

    file_name_import_default = fields.Char(string='Default import file')
    file_name_header_default = fields.Char('Default header file')
    file_name_export_default = fields.Char('Default export file')
    description = fields.Char(string="Description", help="Description of the import model")

    def get_dict(self):
        res = {}
        list_name_uniq = []
        for field in self.field_ids:
            field_name = field.field_import_id.name
            if field_name in list_name_uniq:
                field_name = field.field_import_id.name + '_1'
                list_name_uniq.append(field_name)
            else:
                list_name_uniq.append(field_name)
            if not field.comodel_import_id.id:
                item = (field.name_field_file, field.model_import_id.model, None, None)
            else:
                if not field.field2_comodel_id.id:
                    item = (field.name_field_file, field.model_import_id.model, field.comodel_import_id.model,
                            [(field.field1_comodel_id.name, None)])
                else:
                    item = (field.name_field_file, field.model_import_id.model, field.comodel_import_id.model,
                            [(field.field1_comodel_id.name, None), (field.field2_comodel_id.name, None)])
            res[field_name] = item
        return res

    def chek_model(self):
        list_mess = []
        ir_model_obj = self.env["ir.model.fields"]
        fields = self.field_ids.field_import_id.mapped('name')
        _logger.warning(fields)
        for models in self.order_models():
            for model in models:
                _logger.warning(model)
                fields_model = ir_model_obj.search([('model', '=', model)])
                fields_require = fields_model.filtered(lambda f: f.required  is True)
                _logger.warning(fields_require.mapped('name'))
                ms = "<div> In the {} model, the following fields are required :</div>".format(model)
                list_mess.append(ms)
                ms = ",".join(fields_require.mapped('name'))
                list_mess.append(ms)
                list_mess.append("<div> In the our model for import , the following fields are missing :</div>")

                fields_missing = [fm for fm in fields_require.mapped('name') if fm not in fields_model]
                list_mess.append(",".join(fields_missing))
                _logger.warning(fields_missing)
        comodels = self.field_ids.filtered(lambda f: f.comodel_import_id)
        for field_comodel in comodels:
            list_field = [field_comodel.field1_comodel_id.name, field_comodel.field2_comodel_id.name]
            fields_comodel = ir_model_obj.search([('model', '=', field_comodel.comodel_import_id.model)])
            fields_co_require = fields_comodel.filtered(lambda f: f.required is True)
            _logger.warning(list_field)
            _logger.warning(fields_comodel.mapped('name'))
            _logger.warning(f"reg {fields_co_require.mapped('name')}")
            fields_missing = [fm for fm in fields_co_require.mapped('name') if fm not in list_field]
            _logger.warning(fields_comodel)
            _logger.warning(fields_missing)
        return list_mess

    def get_dict_default(self):
        res = {}
        for field in self.field_default_ids:
            item = (field.value, field.model_import_id.model)
            res[field.field_import_id.name] = item
        return res

    def order_models(self):
        _logger.warning("Models 0")
        # _logger.warning(models)
        models_uniq = []
        models = self.field_ids.model_import_id.mapped('model')
        _logger.warning(models)
        for mod in models:
            if mod not in models_uniq:
                models_uniq.append(mod)
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
                for model_vrel in models:
                    if model_vrel != model:
                        dict_model_order[model] = None
                        field_rel = ir_model_obj.search([("model", "=", model), ("relation", "=", model_vrel)],
                                                        limit=1)
                        if field_rel:
                            if field_rel.ttype == 'many2one':
                                dict_model_order[model] = model_vrel
            _logger.warning(dict_model_order)
            for model, model_val in dict_model_order.items():
                if model_val is None:
                    _logger.warning(model_val)
                    val2 = [key for key, value in dict_model_order.items() if value == model]
                    _logger.warning(val2)
                    val1 = [key for key, value in dict_model_order.items() if value == val2]
                    model_rel = [val1[0], val2[0], model_rel]
        else:
            model_rel = None
            _logger.warning(' Number models is no correct')
        return model_rel

    def export_to_csv(self):
        r = self.chek_model()
        r = self.sstop
        exp_class = self.env['export.csv.file']
        exp = exp_class.create({'dict_import_id': self.id})
        return exp.export_csv_data()


class Importfields(models.Model):
    _name = 'import.fields'
    _description = "fields for import"

    dict_import_id = fields.Many2one('import.dict', string='Import Model')

    name_field_file = fields.Char('Name from File')
    model_import_id = fields.Many2one('ir.model', string="Model")
    field_import_id = fields.Many2one('ir.model.fields', string="Field", )
    comodel_import_id = fields.Many2one('ir.model', string="Model")
    field1_comodel_id = fields.Many2one('ir.model.fields', string="Field 1 relational", )
    value1_comodel = fields.Char('Value 1', default=None)
    field2_comodel_id = fields.Many2one('ir.model.fields', string="Field 2 relational", )
    value2_comodel = fields.Char('Value 2', default=None)


class Importdefaultfields(models.Model):
    _name = 'import.default.fields'
    _description = 'default fields for import'

    dict_import_id = fields.Many2one('import.dict', string='Import Model')
    field_import_id = fields.Many2one('ir.model.fields', string="Field", )
    model_import_id = fields.Many2one('ir.model', string="Model")
    value = fields.Char('Value', default=None)
    code = fields.Text('Code ', default=None)

    @api.constrains('code')
    def evaluate_code(self):
        for value in self.sudo().filtered('code'):
            msg = test_python_expr(expr=value.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)


class PrepareCsvForExport(models.TransientModel):
    _name = "export.csv.file"
    _description = "Prepare header for export"

    data_import_id = fields.Many2one("import.data", string='Import data')
    choose_file = fields.Binary(help="Select CSV file to upload.")
    file_name = fields.Char(help="Name of CSV file.")
    dict_import_id = fields.Many2one('import.dict', string='Import dictionary')

    def export_csv_data(self, data=None):
        """
        This method is used for export the header in csv file.
        :param self:
        :param e.

        """

        buffer = StringIO()
        delimiter, field_names = self.prepare_csv_file_header_and_delimiter()

        csv_writer = csv.DictWriter(buffer, field_names, delimiter=delimiter)
        csv_writer.writer.writerow(field_names)

        if data:
            csv_writer.writerows(data)
        buffer.seek(0)
        file_data = buffer.read().encode()
        if data:
            file_name = self.data_import_id.dict_import_id.file_name_export_default
        else:
            file_name = self.dict_import_id.file_name_header_default

        self.write({
            "choose_file": base64.encodebytes(file_data),
            "file_name": file_name
        })
        _logger.warning("Is downloading")

        return {
            "type": "ir.actions.act_url",
            "url": "web/content/?model=export.csv.file&id=%s&field=choose_file&download=true&"
                   "filename=%s" % (self.id, self.file_name),
            "target": self
        }

    def prepare_csv_file_header_and_delimiter(self):
        """ This method is used to prepare a csv file header and delimiter.
            @return: delimiter, field_names
        """
        delimiter = ","
        if self.dict_import_id:
            header_generic = self.dict_import_id.get_dict()
        else:
            header_generic = self.data_import_id.dict_import_id.get_dict()
        header_generic = {key: val for key, val in header_generic.items() if val != 0}
        field_names = [val[0] for val in header_generic.values()]

        return delimiter, field_names
