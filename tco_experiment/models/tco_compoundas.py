# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class tco_compoundas(models.Model):
    _name = 'tco.compoundas'
    _description = "Compound A"

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char('name')

    task_id = fields.Many2one('tco.task', string='Task')
    project_id = fields.Many2one('tco.project', string='Project Material')

    clm_compound = fields.Char('Compound')
    product_id = fields.Many2one('product.product', string='Material', required=True)
    clm_materialname = fields.Text(string='Name')

    clm_phr = fields.Float(string='PHR')

    clm_weight = fields.Float('Weight')
    clm_formula = fields.Selection([('a', 'A'),
                             ('b', 'B'),
                             ('c', 'C'),
                             ('d', 'D'),
                             ('e', 'E'),
                             ('f', 'F'),
                             ('g', 'G'),
                             ('h', 'H'),
                             ('i', 'I')
                             ], string="Formula Category", store=True)

    def _update_line(self, values):
        Mappeds = self.mapped('task_id')
        for Mapped in Mappeds:
            update_lines = self.filtered(lambda x: x.task_id == Mapped)
            msg = "<b>" + _("The product value has been updated.") + "</b><ul>"
            for line in update_lines:
                old_value = new_value = line.product_id.default_code
                if 'product_id' in values:
                    new_value = self.env['product.product'].search([('id', '=', values["product_id"])]).default_code
                    """values["product_id"]"""
                    """1330706"""
                    # msg += _("product: %(old_qty)s -> %(new_qty)s", old_qty=old_value, new_qty=new_value) + "<br/>" # odoo V15
                    msg += _("product: %s -> %s" % (old_value, new_value)) + "<br/>" # odoo V13
                else:
                    msg += "<li> %s: " % line.product_id.default_code

                old_value = new_value = line.clm_weight
                if 'clm_weight' in values:
                    new_value = values["clm_weight"]
                    # msg += _("weight: %(old_qty)s -> %(new_qty)s", old_qty=old_value, new_qty=new_value) + "<br/>" # odoo V15
                    msg += _("weight: %s -> %s" % (old_value, new_value)) + "<br/>" # odoo V13
            msg += "</ul>"
            Mapped.message_post(body=msg)

    def write(self, values):
        result = super(tco_compoundas, self).write(values)
        if 'clm_weight' or 'product_id' in values:
            self._update_line(values)
        return result