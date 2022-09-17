# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class tco_specific(models.Model):
    _name = "tco.specific"
    _description = "Specific"

    name = fields.Char(related="clm_method_line_id.name")
    sequence = fields.Integer(string='Sequence', default=1)
    project_id = fields.Many2one('tco.project', string='project ID', readonly=True, copy=False, tracking=True)
    clm_method_line_id = fields.Many2one('tco.compound.method.line', string='Method Request', store=True, tracking=True)
    clm_request_value = fields.Char('Request Value', tracking=True)

    def name_get(self):
        result = []
        strintercode1 = ""
        strintercode2 = ""
        strcode1 = ""
        strcode2 = ""
        strunit1 = ""
        strunit2 = ""
        for record in self:
            if record.clm_method_line_id.clm_internal_code:
                strintercode1 = "["
                strintercode2 = "]"
            if record.clm_method_line_id.clm_method_id.clm_Code:
                strcode1 = "["
                strcode2 = "]"
            if record.clm_method_line_id.clm_Unit:
                strunit1 = "("
                strunit2 = ")"
            name = strintercode1 + (record.clm_method_line_id.clm_internal_code or '') + strintercode2 \
                   + strcode1 + (record.clm_method_line_id.clm_method_id.clm_Code or '') + strcode2 \
                   + (record.clm_method_line_id.clm_Method_Standarder or '') \
                   + strunit1 + (record.clm_method_line_id.clm_Unit or '') + strunit2
            result.append((record.id, name))
        return result

    # ---------odoo V15----------------------
    # @api.ondelete(at_uninstall=False)
    # def _unlink_method_line(self):
    #     if self.env['tco.result'].search([('clm_method_line_id', 'in', self.ids)], limit=1):
    #         raise UserError(_('Used by Task (Physical properties result).'))

    # ---------odoo V13----------------------
    def unlink(self):
        if self.env['tco.result'].search([('clm_method_line_id', 'in', self.ids)], limit=1):
            raise UserError(_('Used by Task (Physical properties result).'))
        return super(tco_specific, self).unlink()

    def _update_line(self, values):
        Mappeds = self.mapped('project_id')
        for Mapped in Mappeds:
            update_lines = self.filtered(lambda x: x.project_id == Mapped)
            msg = "<b>" + _("The method specific has been updated.") + "</b><ul>"
            for line in update_lines:
                msg += "<li> %s: " % line.clm_method_line_id.name
                # msg += _("Method specific: %(old_qty)s -> %(new_qty)s ",old_qty=line.clm_request_value,new_qty=values["clm_request_value"]) #odoo V15
                msg += _("Method specific: %s -> %s " % (line.clm_request_value, values["clm_request_value"])) #odoo V13
            msg += "</ul>"
            Mapped.message_post(body=msg)

    def write(self, values):
        if 'clm_request_value' in values:
            self._update_line(values)
        result = super(tco_specific, self).write(values)
        return result