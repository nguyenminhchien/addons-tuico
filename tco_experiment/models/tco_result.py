# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class tco_result(models.Model):
    _name = "tco.result"
    _description = "Result"

    name = fields.Char(store=True, help="name=test_sample + compound_type + astm_code2 + method_standarder")
    display_name = fields.Char(store=True, help="name =test_sample + compound_type + astm_code2 + method_title_id.name + method_standarder")
    sequence = fields.Integer(string='Sequence', default=1)
    task_id = fields.Many2one('tco.task', string='Task ID', readonly=True, copy=False)
    project_id = fields.Many2one('tco.project', store=True, help="Use only get Method Request tco_specific in project")

    task_id_compound = fields.Char(string='Task Name', store=True, related="task_id.clm_compound_id")

    clm_method_line_id = fields.Many2one('tco.specific', string='Method Request', domain="[('project_id','=',project_id.id)]", help="This ID of tco_specific.id") # chuyen sang specific_id thi Xoa

    specific_id = fields.Many2one('tco.specific', string='Method Request',
                                      help="This ID of tco_specific.id", store=True)  # se dung field nay



    method_line_id = fields.Many2one('tco.compound.method.line', store=True, help="Use only get data")
    method_id = fields.Many2one('tco.compound.method', store=True, help="Use only get clm_method_id for method_id")

    result_compound_type = fields.Char(store=True, help="Use only get compound_type for ASTM Code 1")
    result_test_sample = fields.Char(string="Test Sample", store=True, help="Use only get internal_code for test_sample")
    result_astm_code2 = fields.Char(string="astm_code2", store=True, help="Use only get astm_code2 for astm_code2")

    clm_request_value = fields.Char('Request Value', store=True, help="Use only get data")

    result_unit = fields.Char(string='Unit', store=True)
    result_version = fields.Integer(string='Version', store=True)
    result_year = fields.Integer(string='At Year', store=True)

    result_num = fields.Float('Result Value', required=True, help="Input Result Value of method in Task ID")

    clm_result_value = fields.Char('Result Value', help="Not Use. Input min~max and return for (min_value, max_value) fields")
    clm_result_min_value = fields.Float('Min Value', help="Not Use")
    clm_result_max_value = fields.Float('Max Value', help="Not Use")
    clm_result = fields.Selection([('ok', 'OK'), ('ng', 'NG')], default="ng")

    def _update_line(self, values):
        Mappeds = self.mapped('task_id')
        for Mapped in Mappeds:
            update_lines = self.filtered(lambda x: x.task_id == Mapped)
            msg = "<b>" + _("The method result has been updated.") + "</b><ul>"
            for line in update_lines:
                msg += "<li> %s: " % line.specific_id.name
                old_value = new_value = line.clm_result_value
                if 'clm_result_value' in values:
                    new_value = values["clm_result_value"]
                    # msg += _("Method result: %(old_qty)s -> %(new_qty)s ", old_qty=old_value, new_qty=new_value) #odoo V15
                    msg += _("Method result: %s -> %s " % (old_value, new_value)) #odoo V13
                old_value = new_value = line.clm_result
                if 'clm_result' in values:
                    new_value = values["clm_result"]
                    # msg += _("result: %(old_qty)s -> %(new_qty)s ", old_qty=old_value, new_qty=new_value) #odoo V15
                    msg += _("result: %s -> %s " % (old_value, new_value,)) #odoo V13
            msg += "</ul>"
            Mapped.message_post(body=msg)

    def write(self, values):
        if 'clm_result_value' or 'clm_result' in values:
            self._update_line(values)
        result = super(tco_result, self).write(values)
        return result

    @api.onchange('specific_id')
    def _compute_get_value(self):
        for record in self:
            if record.specific_id:
                if record.project_id:
                    record.result_compound_type = record.project_id.compound_type

                record.method_line_id = record.specific_id.clm_method_line_id.id
                record.method_id = record.specific_id.clm_method_line_id.clm_method_id.id
                record.result_test_sample = record.specific_id.clm_method_line_id.clm_internal_code

                record.result_astm_code2 = record.method_line_id.astm_code2
                record.clm_request_value = record.specific_id.clm_request_value
                record.result_unit = record.specific_id.specific_unit
                record.result_version = record.specific_id.specific_version
                record.result_year = record.specific_id.specific_year

                name = ""
                if record.result_test_sample:
                    name = "%s[%s]" % (name, record.result_test_sample)
                if record.result_compound_type:
                    name = "%s[%s]" % (name, record.result_compound_type)
                if record.result_astm_code2:
                    name = "%s[%s]" % (name, record.result_astm_code2)
                if record.method_id:
                    name = "%s%s" % (name, record.method_id.name)
                if record.method_line_id:
                    name = "%s%s" % (name, record.method_line_id.clm_Method_Standarder)
                record.display_name = name
                record.name = name


    def name_get(self):
        result = []
        for res in self:
            name = res.specific_id.name
            result.append((res.id, name))
        return result

    def action_view_form_task(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'tco.task',
            'res_id': self.task_id.id,
        }

    def get_default_context(self):
        self.ensure_one()
        ctx = {
        }
        return ctx

    def edit_record(self):
        self.ensure_one()

        ctx = self.get_default_context()
        return {
            'name': _('Edit Line'),
            'view_mode': 'form',
            'res_model': 'tco.result',
            'res_id': self.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    @api.depends('clm_result_value')
    def _compute_result_value(self):
        for record in self:
            fl_min = 0.0
            fl_max = 0.0
            if record.clm_result_value:
                strcap = record.clm_result_value
                # ---------bat loi chuyen kieu khong duoc-----------
                try:
                    if float(strcap) != 0.0:
                        fl_min = fl_max = float(strcap)
                except Exception:
                    fl_min = fl_max = 0.0
                if strcap.find('~'):
                    arrstrcap = strcap.split('~')
                    for i in range(len(arrstrcap)):
                        if i == 0:
                            fl_min = fl_max = float(arrstrcap[i])
                        if i == 1:
                            if float(arrstrcap[i]) > 0:
                                fl_max = float(arrstrcap[i])
            record['clm_result_min_value'] = fl_min
            record['clm_result_max_value'] = fl_max

        # use update database
        # --update tco_result set
        #     clm_result_min_value = (clm_result_value)::numeric,
        # --  clm_result_max_value = (clm_result_value)::numeric
        # --where clm_result_value ilike '%~%'
        # --update tco_result set clm_result_min_value = cast_to_float(clm_result_value),
        # --                        clm_result_max_value = cast_to_float(clm_result_value)
        # --where cast_to_float(clm_result_value) <> 0
