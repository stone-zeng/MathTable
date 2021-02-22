# encoding: utf-8

###########################################################################################################
#
#
#	Palette Plugin: Math Table
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from vanilla import *


class MathTable(PalettePlugin):

	@objc.python_method
	def settings(self):
		self.name = 'Math Table'

		# Describe the layout of the Math panel
		italicCorrection        = Group('auto')
		topAccentPosition       = Group('auto')
		extendedShape           = Group('auto')
		italicCorrection.label  = TextBox('auto', 'Italic Correction', sizeStyle='small')
		topAccentPosition.label = TextBox('auto', 'Top Accent Position', sizeStyle='small')
		extendedShape.label     = TextBox('auto', 'Extended Shape', sizeStyle='small')
		italicCorrection.text   = EditText('auto', placeholder='0', sizeStyle='small')
		topAccentPosition.text  = EditText('auto', placeholder='0', sizeStyle='small')
		extendedShape.checkBox  = CheckBox('auto', title='', sizeStyle='small')

		rules = lambda t: [
			# Horizontal
			'H:|[label(110)]-10-[{}(>=30)]|'.format(t),
			# Vertical
			'V:|[label(20)]|',
			'V:|[{}]|'.format(t),
		]
		italicCorrection.addAutoPosSizeRules(rules('text'))
		topAccentPosition.addAutoPosSizeRules(rules('text'))
		extendedShape.addAutoPosSizeRules(rules('checkBox'))

		# Create Vanilla window and group with controls
		self.paletteView = Window((200, 100))
		self.paletteView.group = Group('auto')
		self.paletteView.group.italicCorrection = italicCorrection
		self.paletteView.group.topAccentPosition = topAccentPosition
		self.paletteView.group.extendedShape = extendedShape
		self.paletteView.group.addAutoPosSizeRules([
			# Horizontal
			'H:|-10-[italicCorrection]|',
			'H:|-10-[topAccentPosition]|',
			'H:|-10-[extendedShape]|',
			# Vertical
			'V:|-2-[italicCorrection][topAccentPosition][extendedShape]|',
		])

		# Set dialog to NSView
		self.dialog = self.paletteView.group.getNSView()

	@objc.python_method
	def start(self):
		Glyphs.addCallback(self.update, UPDATEINTERFACE)
		Glyphs.addCallback(self.draw, DRAWFOREGROUND)

	@objc.python_method	
	def __del__(self):
		Glyphs.removeCallback(self.update)
		Glyphs.removeCallback(self.draw)

	@objc.python_method
	def update(self, sender):
		pass
		# TODO:
		# font = sender.object().parent
		# if font:
		# 	if font.currentTab:
		# 		# In the Edit View
		# 		print('In the Edit View')
		# 	else:
		# 		print(font.selection)

	@objc.python_method
	def draw(self, layer, info):
		# Due to internal Glyphs.app structure, we need to catch and print exceptions
		# of these callback functions with try/except like so:
		try:
			self.drawTopAccentPosition(layer)
		# Error. Print exception.
		except:
			import traceback
			print(traceback.format_exc())

	@objc.python_method
	def getScale(self):
		return Glyphs.font.currentTab.scale

	@objc.python_method
	def getViewInfo(self):
		'''Return the origin and size of the visible area of the Edit view.
		'''
		scale = self.getScale()
		view = Glyphs.font.currentTab.graphicView()
		visibleRect = view.visibleRect()
		activePosition = view.activePosition()
		viewOriginX = (visibleRect.origin.x - activePosition.x) / scale
		viewOriginY = (visibleRect.origin.y - activePosition.y) / scale
		viewWidth = visibleRect.size.width / scale
		viewHeight = visibleRect.size.height / scale
		return ((viewOriginX, viewOriginY), (viewWidth, viewHeight))

	@objc.python_method
	def drawTextAtPoint(self, text, pos, size=10.0, color=NSColor.textColor()):
		attributes = {
			NSFontAttributeName: NSFont.labelFontOfSize_(size / self.getScale()),
			NSForegroundColorAttributeName: color,
		}
		displayText = NSAttributedString.alloc().initWithString_attributes_(text, attributes)
		displayText.drawAtPoint_(pos)

	@objc.python_method
	def drawTopAccentPosition(self, layer):
		if layer.userData:
			if 'math' in layer.userData:
				if 'topAccent' in layer.userData['math']:
					topAccent = layer.userData['math']['topAccent']
					((_, y), (_, viewHeight)) = self.getViewInfo()
					scale = self.getScale()

					color = NSColor.systemGreenColor()
					color.set()

					path = NSBezierPath.bezierPath()
					path.moveToPoint_((topAccent, y))
					path.lineToPoint_((topAccent, y + viewHeight))
					path.setLineWidth_(1 / scale)
					path.stroke()

					textPos = (topAccent + 4, y + viewHeight - 75 / scale)
					print(textPos)
					self.drawTextAtPoint('MATH: Top Accent', textPos, size=11, color=color)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
