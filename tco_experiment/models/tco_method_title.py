from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError



class tco_method_title(models.Model):
    _name = "tco.method.title"
    _description = "Method Title"

    name = fields.Char(string='Method Group', compute="_compute_get_name", required=True, store=True, index=True)

    grouptitle = fields.Selection([('0', 'Basic Physical Properties'),
                                 ('A', 'Heat Resistance'),
                                 ('B', 'Comression Set'),
                                 ('EA', 'Water Resistance'),
                                   ('EF1', 'Fuel A Resistance'),
                                   ('EF2', 'Fuel B Resistance'),
                                   ('EF3', 'Fuel C Resistance'),
                                   ('EO1', 'IRM 901 Oil Resistance'),
                                   ('EO3', 'IRM 903 Oil Resistance'),
                                   ('EO7', 'Fluid No.101 Resistance'),
                                   ('EO8', 'Service Liquid No.101 Resistance'),
                                   ('G1', 'Tear Resistance, Die B'),
                                   ('G2', 'Tear Resistance, Die C'),
                                   ('F1', 'Low-temperature Resistance'),
                                   ('PC', 'Process condition'),

                                 ], string="Title", default="0")

    timevalue = fields.Float(string='Time Value', store=True)
    timeunit = fields.Selection([('hrs', 'Hrs'),
                             ('day', 'Day'),
                             ('min', 'Min')
                             ], string="Time Unit", default="hrs")

    tempvalue = fields.Float(string='Temperature Value')
    tempunit = fields.Selection([('c', 'ºC'),
                             ('f', 'ºF')
                             ], string="Temperature Unit", default="c")
    
    _sql_constraints = [(
        'unique_method_name',
        'unique (name)',
        'Method name double key. please check!')
    ]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result

    # def _get_compound_method_name_for_task(self, task_id):
    #     result =[]
    #     self._cr.execute(
    #         "select distinct tmt.id, tmt.name "
    #         "from tco_result tr "
    #         "inner join tco_specific ts on ts.id = tr.clm_method_line_id "
    #         "inner join tco_compound_method_line tcml on ts.clm_method_line_id = tcml.id "
    #         "inner join tco_compound_method tcm on tcm.id = tcml.clm_method_id "
    #         "inner join tco_method_title tmt  on tcm.method_title_id = tmt.id "
    #         "where tr.task_id = %s",
    #         (task_id,))
    #     result = tuple([rec['id'] for rec in self._cr.dictfetchall()])
    #     return tuple(result)



    def _compute_name(self, grouptitle, timevalue, timeunit, tempvalue, tempunit):
        name = ""
        if grouptitle:
            name = dict(self._fields['grouptitle'].selection).get(self.grouptitle)
        if timevalue or 0 > 0:
            name += ", %s" % int(timevalue)
            if timeunit:
                name += " %s" % dict(self._fields['timeunit'].selection).get(self.timeunit)
        if tempvalue or 0 > 0:
            name += " at %s" % int(tempvalue)
            if tempunit:
                name += " %s" % dict(self._fields['tempunit'].selection).get(self.tempunit)
        return name

    @api.depends('grouptitle', 'timevalue', 'timeunit', 'tempvalue', 'tempunit')
    def _compute_get_name(self):
        for record in self:
            record.name = record._compute_name(record.grouptitle, record.timevalue, record.timeunit, record.tempvalue, record.tempunit)

#
# selection_field = fields.Selection([("1", "One"),("2", "Two"),("3","Three"),],string="Selection")
#
# string_value = dict(self._fields['selection_field'].selection).get(self.selection_field))
#
# In qweb:-
#
# <t t-esc="dict(docs.fields_get(allfields=['selection_field'])['selection_field']['selection'])[docs.selection_field]"/>