# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class tco_result(models.Model):
    _name = "tco.result"
    _description = "Result"

    name = fields.Char(related="clm_method_line_id.name")
    sequence = fields.Integer(string='Sequence', default=1)
    task_id = fields.Many2one('tco.task', string='Task ID', readonly=True, copy=False)
    project_id = fields.Integer(related="task_id.project_id.id")
    task_id_compound = fields.Char(string='Task Name', related="task_id.clm_compound_id", store=True)

    clm_method_line_id = fields.Many2one('tco.specific', string='Method Request', domain="[('project_id','=',project_id)]")

    clm_request_value = fields.Char('Request Value', related="clm_method_line_id.clm_request_value")
    clm_result_value = fields.Char('Result Value')
    clm_result_min_value = fields.Float('Min Value')
    clm_result_max_value = fields.Float('Max Value')
    clm_result = fields.Selection([('ok', 'OK'), ('ng', 'NG')], default="ng")

    def _update_line(self, values):
        Mappeds = self.mapped('task_id')
        for Mapped in Mappeds:
            update_lines = self.filtered(lambda x: x.task_id == Mapped)
            msg = "<b>" + _("The method result has been updated.") + "</b><ul>"
            for line in update_lines:
                msg += "<li> %s: " % line.clm_method_line_id.name
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


    def name_get(self):
        result = []
        for res in self:
            name = res.clm_method_line_id.name
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

    @api.onchange('clm_result_value')
    def _onchange_result_value(self):
        fl_min = 0.0
        fl_max = 0.0
        if self.clm_result_value:
            strcap = self.clm_result_value
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
        self.clm_result_min_value = fl_min
        self.clm_result_max_value = fl_max

        # use update database
        # --update tco_result set
        #     clm_result_min_value = (clm_result_value)::numeric,
        # --  clm_result_max_value = (clm_result_value)::numeric
        # --where clm_result_value ilike '%~%'
        # --update tco_result set clm_result_min_value = cast_to_float(clm_result_value),
        # --                        clm_result_max_value = cast_to_float(clm_result_value)
        # --where cast_to_float(clm_result_value) <> 0
