# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models


class Resolution(models.Model):
    _name = 'repair.resolution'
    _description = 'Repair resolution'
    _rec_name = 'resolution_name'
    resolution_name = fields.Char(string="Resolution name")
