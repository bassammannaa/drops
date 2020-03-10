# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = "product.category"

    name_ar = fields.Char(string="Name Arabic", required=False, )
    old_id = fields.Integer(string="Old ID", required=False,)
    old_parent_id = fields.Integer(string="Old Parent ID", required=False, )
