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
import traceback
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
		italicCorrection.text   = EditText('auto', placeholder='Empty', sizeStyle='small', continuous=False, callback=self.italicCorrectionCallback)
		topAccentPosition.text  = EditText('auto', placeholder='Empty', sizeStyle='small', continuous=False, callback=self.topAccentCallback)
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
			'H:|-10-[italicCorrection]-|',
			'H:|-10-[topAccentPosition]-|',
			'H:|-10-[extendedShape]-|',
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
		Glyphs.removeCallback(self.italicCorrectionCallback)
		Glyphs.removeCallback(self.topAccentCallback)

	@objc.python_method
	def update(self, sender):
		if font := sender.object().parent:
			layers = font.selectedLayers
			self._updateHelper(layers, self.paletteView.group.italicCorrection.text, 'italicCorrection')
			self._updateHelper(layers, self.paletteView.group.topAccentPosition.text, 'topAccent')

	@objc.python_method
	def _updateHelper(self, layers, text, entry):
		if layers:
			valueList = []
			for layer in layers:
				mathTable = layer.userData['math']
				if mathTable and entry in mathTable:
					valueList.append(mathTable[entry])
				else:
					valueList.append('Empty')
			if len(set(valueList)) == 1:
				if valueList[0] == 'Empty':
					text.set('')
					text.setPlaceholder('Empty')
				else:
					text.set(str(valueList[0]))
			else:
				text.set('')
				text.setPlaceholder('Multiple Values')
		else:
			text.set('')
			text.setPlaceholder('No Selection')

	@objc.python_method
	def draw(self, layer, info):
		try:
			self.drawTopAccentPosition(layer)
		except:
			print(traceback.format_exc())

	@objc.python_method
	def italicCorrectionCallback(self, sender):
		if sender.get() == '':
			if layers := Glyphs.font.selectedLayers:
				for layer in layers:
					mathTableDelete(layer, 'italicCorrection')
		else:
			val = toInt(sender.get())
			if layers := Glyphs.font.selectedLayers:
				for layer in layers:
					mathTableInsert(layer, 'italicCorrection', val)

	@objc.python_method
	def topAccentCallback(self, sender):
		if sender.get() == '':
			if layers := Glyphs.font.selectedLayers:
				for layer in layers:
					mathTableDelete(layer, 'topAccent')
		else:
			val = toInt(sender.get())
			if layers := Glyphs.font.selectedLayers:
				for layer in layers:
					mathTableInsert(layer, 'topAccent', val)

	@objc.python_method
	def getScale(self):
		'''Return the current scale factor of the Edit View UI.'''
		return Glyphs.font.currentTab.scale

	@objc.python_method
	def getViewInfo(self):
		'''Return the origin and size of the visible area of the Edit view.'''
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
		if mathTable := layer.userData['math']:
			if 'topAccent' in mathTable:
				topAccent = mathTable['topAccent']
				scale = self.getScale()
				((_, y), (_, viewHeight)) = self.getViewInfo()

				color = NSColor.systemGreenColor()
				color.set()

				path = NSBezierPath.bezierPath()
				path.moveToPoint_((topAccent, y))
				path.lineToPoint_((topAccent, y + viewHeight))
				path.setLineWidth_(1 / scale)
				path.stroke()

				textPos = (topAccent + 4, y + viewHeight - 75 / scale)
				self.drawTextAtPoint('MATH: Top Accent', textPos, size=11, color=color)

	@objc.python_method
	def __file__(self):
		return __file__

def mathTableInsert(layer, key, val):
	'''Insert key-value pair into MATH table of `layer`.'''
	if mathTable := layer.userData['math']:
		mathTable[key] = val
	else:
		layer.userData['math'] = {key: val}

def mathTableDelete(layer, key):
	'''Delete key in MATH table of `layer`.'''
	if mathTable := layer.userData['math']:
		if key in mathTable:
			del mathTable[key]

def toInt(s: str):
	'''Safely convert a string to integer.'''
	try:
		return int(s)
	except ValueError:
		try:
			return round(float(s))
		except ValueError:
			return 0
