# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import xlrd
import tempfile
import base64

logger = logging.getLogger(__name__)


class VendorsUpload(models.TransientModel):
    _name = "drops.vendors.upload"
    _description = "Vendors Upload"

    data = fields.Binary('File', required=True, attachment=False)
    filename = fields.Char('File Name', required=True)
    overwrite = fields.Boolean('Overwrite Existing Date',
                               default=True,)

    def import_data(self):
        try:
            # Open File for read
            #=====================
            file_path = tempfile.gettempdir() + '/file.xls'
            f = open(file_path, 'wb')
            f.write(base64.decodebytes(self.data))
            f.close()
            book = xlrd.open_workbook(file_path)

            # Validations
            #=============
            if book.nsheets != 1:
                raise ValidationError("Number of Excel book is less or more than one book.")

            sheet = book.sheet_by_index(0)
            if sheet.ncols != 7:
                raise ValidationError("Number of book Columns are less or more than 7 columns.")
            if sheet.nrows < 2:
                raise ValidationError("Number of book records are less or more than 1 row.")


            # Clear data
            # =============
            res_partner_obj = self.env['res.partner'].search([('old_id', '>=', 0)])
            for res_partner in res_partner_obj:
                res_partner.unlink()


            # Upload Data
            # =============
            for row_num in range(sheet.nrows):
                if row_num == 0:
                    continue

                self.env['res.partner'].create({'old_id': sheet.row(row_num)[0].value,
                                                     'name': sheet.row(row_num)[1].value,
                                                     'name_ar': sheet.row(row_num)[2].value,
                                                     'email': sheet.row(row_num)[3].value,
                                                     'mobile': sheet.row(row_num)[4].value,
                                                     'phone': sheet.row(row_num)[5].value,
                                                     'active': (True if int(sheet.row(row_num)[6].value) == 1 else False),
                                                     'is_company': 'true',
                                                     'supplier_rank': 1, })

        except Exception as e:
            logger.exception("import_data Method")
            raise ValidationError(e)


