define("simple-html-tokenizer/entity-parser", ["exports", "module"], function (exports, module) {
  "use strict";

  function EntityParser(named) {
    this.named = named;
  }

  var HEXCHARCODE = /^#[xX]([A-Fa-f0-9]+)$/;
  var CHARCODE = /^#([0-9]+)$/;
  var NAMED = /^([A-Za-z0-9]+)$/;

  EntityParser.prototype.parse = function (entity) {
    if (!entity) {
      return;
    }
    var matches = entity.match(HEXCHARCODE);
    if (matches) {
      return "&#x" + matches[1] + ";";
    }
    matches = entity.match(CHARCODE);
    if (matches) {
      return "&#" + matches[1] + ";";
    }
    matches = entity.match(NAMED);
    if (matches) {
      return "&" + matches[1] + ";";
    }
  };

  module.exports = EntityParser;
});
define('simple-html-tokenizer/evented-tokenizer', ['exports', 'module', './utils'], function (exports, module, _utils) {
  'use strict';

  function EventedTokenizer(delegate, entityParser) {
    this.delegate = delegate;
    this.entityParser = entityParser;

    this.state = null;
    this.input = null;

    this.index = -1;
    this.line = -1;
    this.column = -1;
    this.tagLine = -1;
    this.tagColumn = -1;

    this.reset();
  }

  EventedTokenizer.prototype = {
    reset: function reset() {
      this.state = 'beforeData';
      this.input = '';

      this.index = 0;
      this.line = 1;
      this.column = 0;

      this.tagLine = -1;
      this.tagColumn = -1;

      this.delegate.reset();
    },

    tokenize: function tokenize(input) {
      this.reset();
      this.tokenizePart(input);
      this.tokenizeEOF();
    },

    tokenizePart: function tokenizePart(input) {
      this.input += _utils.preprocessInput(input);

      while (this.index < this.input.length) {
        this.states[this.state].call(this);
      }
    },

    tokenizeEOF: function tokenizeEOF() {
      this.flushData();
    },

    flushData: function flushData() {
      if (this.state === 'data') {
        this.delegate.finishData();
        this.state = 'beforeData';
      }
    },

    peek: function peek() {
      return this.input.charAt(this.index);
    },

    consume: function consume() {
      var char = this.peek();

      this.index++;

      if (char === "\n") {
        this.line++;
        this.column = 0;
      } else {
        this.column++;
      }

      return char;
    },

    consumeCharRef: function consumeCharRef() {
      var endIndex = this.input.indexOf(';', this.index);
      if (endIndex === -1) {
        return;
      }
      var entity = this.input.slice(this.index, endIndex);
      var chars = this.entityParser.parse(entity);
      if (chars) {
        this.index = endIndex + 1;
        return chars;
      }
    },

    markTagStart: function markTagStart() {
      this.tagLine = this.line;
      this.tagColumn = this.column;
    },

    states: {
      beforeData: function beforeData() {
        var char = this.peek();

        if (char === "<") {
          this.state = 'tagOpen';
          this.markTagStart();
          this.consume();
        } else {
          this.state = 'data';
          this.delegate.beginData();
        }
      },

      data: function data() {
        var char = this.peek();

        if (char === "<") {
          this.delegate.finishData();
          this.state = 'tagOpen';
          this.markTagStart();
          this.consume();
        } else if (char === "&") {
          this.consume();
          this.delegate.appendToData(this.consumeCharRef() || "&");
        } else {
          this.consume();
          this.delegate.appendToData(char);
        }
      },

      tagOpen: function tagOpen() {
        var char = this.consume();

        if (char === "!") {
          this.state = 'markupDeclaration';
        } else if (char === "/") {
          this.state = 'endTagOpen';
        } else if (_utils.isAlpha(char)) {
          this.state = 'tagName';
          this.delegate.beginStartTag();
          this.delegate.appendToTagName(char.toLowerCase());
        }
      },

      markupDeclaration: function markupDeclaration() {
        var char = this.consume();

        if (char === "-" && this.input.charAt(this.index) === "-") {
          this.index++;
          this.state = 'commentStart';
          this.delegate.beginComment();
        }
      },

      commentStart: function commentStart() {
        var char = this.consume();

        if (char === "-") {
          this.state = 'commentStartDash';
        } else if (char === ">") {
          this.delegate.finishComment();
          this.state = 'beforeData';
        } else {
          this.delegate.appendToCommentData(char);
          this.state = 'comment';
        }
      },

      commentStartDash: function commentStartDash() {
        var char = this.consume();

        if (char === "-") {
          this.state = 'commentEnd';
        } else if (char === ">") {
          this.delegate.finishComment();
          this.state = 'beforeData';
        } else {
          this.delegate.appendToCommentData("-");
          this.state = 'comment';
        }
      },

      comment: function comment() {
        var char = this.consume();

        if (char === "-") {
          this.state = 'commentEndDash';
        } else {
          this.delegate.appendToCommentData(char);
        }
      },

      commentEndDash: function commentEndDash() {
        var char = this.consume();

        if (char === "-") {
          this.state = 'commentEnd';
        } else {
          this.delegate.appendToCommentData("-" + char);
          this.state = 'comment';
        }
      },

      commentEnd: function commentEnd() {
        var char = this.consume();

        if (char === ">") {
          this.delegate.finishComment();
          this.state = 'beforeData';
        } else {
          this.delegate.appendToCommentData("--" + char);
          this.state = 'comment';
        }
      },

      tagName: function tagName() {
        var char = this.consume();

        if (_utils.isSpace(char)) {
          this.state = 'beforeAttributeName';
        } else if (char === "/") {
          this.state = 'selfClosingStartTag';
        } else if (char === ">") {
          this.delegate.finishTag();
          this.state = 'beforeData';
        } else {
          this.delegate.appendToTagName(char);
        }
      },

      beforeAttributeName: function beforeAttributeName() {
        var char = this.consume();

        if (_utils.isSpace(char)) {
          return;
        } else if (char === "/") {
          this.state = 'selfClosingStartTag';
        } else if (char === ">") {
          this.delegate.finishTag();
          this.state = 'beforeData';
        } else {
          this.state = 'attributeName';
          this.delegate.beginAttribute();
          this.delegate.appendToAttributeName(char);
        }
      },

      attributeName: function attributeName() {
        var char = this.consume();

        if (_utils.isSpace(char)) {
          this.state = 'afterAttributeName';
        } else if (char === "/") {
          this.delegate.beginAttributeValue(false);
          this.delegate.finishAttributeValue();
          this.state = 'selfClosingStartTag';
        } else if (char === "=") {
          this.state = 'beforeAttributeValue';
        } else if (char === ">") {
          this.delegate.beginAttributeValue(false);
          this.delegate.finishAttributeValue();
          this.delegate.finishTag();
          this.state = 'beforeData';
        } else {
          this.delegate.appendToAttributeName(char);
        }
      },

      afterAttributeName: function afterAttributeName() {
        var char = this.consume();

        if (_utils.isSpace(char)) {
          return;
        } else if (char === "/") {
          this.delegate.beginAttributeValue(false);
          this.delegate.finishAttributeValue();
          this.state = 'selfClosingStartTag';
        } else if (char === "=") {
          this.state = 'beforeAttributeValue';
        } else if (char === ">") {
          this.delegate.beginAttributeValue(false);
          this.delegate.finishAttributeValue();
          this.delegate.finishTag();
          this.state = 'beforeData';
        } else {
          this.delegate.beginAttributeValue(false);
          this.delegate.finishAttributeValue();
          this.state = 'attributeName';
          this.delegate.beginAttribute();
          this.delegate.appendToAttributeName(char);
        }
      },

      beforeAttributeValue: function beforeAttributeValue() {
        var char = this.consume();

        if (_utils.isSpace(char)) {} else if (char === '"') {
          this.state = 'attributeValueDoubleQuoted';
          this.delegate.beginAttributeValue(true);
        } else if (char === "'") {
          this.state = 'attributeValueSingleQuoted';
          this.delegate.beginAttributeValue(true);
        } else if (char === ">") {
          this.delegate.beginAttributeValue(false);
          this.delegate.finishAttributeValue();
          this.delegate.finishTag();
          this.state = 'beforeData';
        } else {
          this.state = 'attributeValueUnquoted';
          this.delegate.beginAttributeValue(false);
          this.delegate.appendToAttributeValue(char);
        }
      },

      attributeValueDoubleQuoted: function attributeValueDoubleQuoted() {
        var char = this.consume();

        if (char === '"') {
          this.delegate.finishAttributeValue();
          this.state = 'afterAttributeValueQuoted';
        } else if (char === "&") {
          this.delegate.appendToAttributeValue(this.consumeCharRef('"') || "&");
        } else {
          this.delegate.appendToAttributeValue(char);
        }
      },

      attributeValueSingleQuoted: function attributeValueSingleQuoted() {
        var char = this.consume();

        if (char === "'") {
          this.delegate.finishAttributeValue();
          this.state = 'afterAttributeValueQuoted';
        } else if (char === "&") {
          this.delegate.appendToAttributeValue(this.consumeCharRef("'") || "&");
        } else {
          this.delegate.appendToAttributeValue(char);
        }
      },

      attributeValueUnquoted: function attributeValueUnquoted() {
        var char = this.consume();

        if (_utils.isSpace(char)) {
          this.delegate.finishAttributeValue();
          this.state = 'beforeAttributeName';
        } else if (char === "&") {
          this.delegate.appendToAttributeValue(this.consumeCharRef(">") || "&");
        } else if (char === ">") {
          this.delegate.finishAttributeValue();
          this.delegate.finishTag();
          this.state = 'beforeData';
        } else {
          this.delegate.appendToAttributeValue(char);
        }
      },

      afterAttributeValueQuoted: function afterAttributeValueQuoted() {
        var char = this.peek();

        if (_utils.isSpace(char)) {
          this.consume();
          this.state = 'beforeAttributeName';
        } else if (char === "/") {
          this.consume();
          this.state = 'selfClosingStartTag';
        } else if (char === ">") {
          this.consume();
          this.delegate.finishTag();
          this.state = 'beforeData';
        } else {
          this.state = 'beforeAttributeName';
        }
      },

      selfClosingStartTag: function selfClosingStartTag() {
        var char = this.peek();

        if (char === ">") {
          this.consume();
          this.delegate.markTagAsSelfClosing();
          this.delegate.finishTag();
          this.state = 'beforeData';
        } else {
          this.state = 'beforeAttributeName';
        }
      },

      endTagOpen: function endTagOpen() {
        var char = this.consume();

        if (_utils.isAlpha(char)) {
          this.state = 'tagName';
          this.delegate.beginEndTag();
          this.delegate.appendToTagName(char.toLowerCase());
        }
      }
    }
  };

  module.exports = EventedTokenizer;
});
define("simple-html-tokenizer/html5-named-char-refs", ["exports", "module"], function (exports, module) {
  "use strict";

  var HTML5NamedCharRefs = {};
  module.exports = HTML5NamedCharRefs;
});
define('simple-html-tokenizer/index', ['exports', './html5-named-char-refs', './entity-parser', './evented-tokenizer', './tokenizer', './tokenize'], function (exports, _html5NamedCharRefs, _entityParser, _eventedTokenizer, _tokenizer, _tokenize) {
  'use strict';

  exports.__esModule = true;

  function _interopRequire(obj) { return obj && obj.__esModule ? obj['default'] : obj; }

  exports.HTML5NamedCharRefs = _interopRequire(_html5NamedCharRefs);
  exports.EntityParser = _interopRequire(_entityParser);
  exports.EventedTokenizer = _interopRequire(_eventedTokenizer);
  exports.Tokenizer = _interopRequire(_tokenizer);
  exports.tokenize = _interopRequire(_tokenize);
});
define('simple-html-tokenizer/tokenize', ['exports', 'module', './tokenizer', './entity-parser', './html5-named-char-refs'], function (exports, module, _tokenizer, _entityParser, _html5NamedCharRefs) {
  'use strict';

  module.exports = tokenize;

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

  var _Tokenizer = _interopRequireDefault(_tokenizer);

  var _EntityParser = _interopRequireDefault(_entityParser);

  var _HTML5NamedCharRefs = _interopRequireDefault(_html5NamedCharRefs);

  function tokenize(input, options) {
    var tokenizer = new _Tokenizer['default'](new _EntityParser['default'](_HTML5NamedCharRefs['default']), options);
    return tokenizer.tokenize(input);
  }
});
define('simple-html-tokenizer/tokenizer', ['exports', 'module', './evented-tokenizer'], function (exports, module, _eventedTokenizer) {
  'use strict';

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

  var _EventedTokenizer = _interopRequireDefault(_eventedTokenizer);

  function Tokenizer(entityParser, options) {
    this.token = null;
    this.startLine = 1;
    this.startColumn = 0;
    this.options = options || {};
    this.tokenizer = new _EventedTokenizer['default'](this, entityParser);
  }

  Tokenizer.prototype = {
    tokenize: function tokenize(input) {
      this.tokens = [];
      this.tokenizer.tokenize(input);
      return this.tokens;
    },

    tokenizePart: function tokenizePart(input) {
      this.tokens = [];
      this.tokenizer.tokenizePart(input);
      return this.tokens;
    },

    tokenizeEOF: function tokenizeEOF() {
      this.tokens = [];
      this.tokenizer.tokenizeEOF();
      return this.tokens[0];
    },

    reset: function reset() {
      this.token = null;
      this.startLine = 1;
      this.startColumn = 0;
    },

    addLocInfo: function addLocInfo() {
      if (this.options.loc) {
        this.token.loc = {
          start: {
            line: this.startLine,
            column: this.startColumn
          },
          end: {
            line: this.tokenizer.line,
            column: this.tokenizer.column
          }
        };
      }
      this.startLine = this.tokenizer.line;
      this.startColumn = this.tokenizer.column;
    },

    // Data

    beginData: function beginData() {
      this.token = {
        type: 'Chars',
        chars: ''
      };
      this.tokens.push(this.token);
    },

    appendToData: function appendToData(char) {
      this.token.chars += char;
    },

    finishData: function finishData() {
      this.addLocInfo();
    },

    // Comment

    beginComment: function beginComment() {
      this.token = {
        type: 'Comment',
        chars: ''
      };
      this.tokens.push(this.token);
    },

    appendToCommentData: function appendToCommentData(char) {
      this.token.chars += char;
    },

    finishComment: function finishComment() {
      this.addLocInfo();
    },

    // Tags - basic

    beginStartTag: function beginStartTag() {
      this.token = {
        type: 'StartTag',
        tagName: '',
        attributes: [],
        selfClosing: false
      };
      this.tokens.push(this.token);
    },

    beginEndTag: function beginEndTag() {
      this.token = {
        type: 'EndTag',
        tagName: ''
      };
      this.tokens.push(this.token);
    },

    finishTag: function finishTag() {
      this.addLocInfo();
    },

    markTagAsSelfClosing: function markTagAsSelfClosing() {
      this.token.selfClosing = true;
    },

    // Tags - name

    appendToTagName: function appendToTagName(char) {
      this.token.tagName += char;
    },

    // Tags - attributes

    beginAttribute: function beginAttribute() {
      this._currentAttribute = ["", "", null];
      this.token.attributes.push(this._currentAttribute);
    },

    appendToAttributeName: function appendToAttributeName(char) {
      this._currentAttribute[0] += char;
    },

    beginAttributeValue: function beginAttributeValue(isQuoted) {
      this._currentAttribute[2] = isQuoted;
    },

    appendToAttributeValue: function appendToAttributeValue(char) {
      this._currentAttribute[1] = this._currentAttribute[1] || "";
      this._currentAttribute[1] += char;
    },

    finishAttributeValue: function finishAttributeValue() {}
  };

  module.exports = Tokenizer;
});
define("simple-html-tokenizer/utils", ["exports"], function (exports) {
  "use strict";

  exports.__esModule = true;
  exports.isSpace = isSpace;
  exports.isAlpha = isAlpha;
  exports.preprocessInput = preprocessInput;
  var WSP = /[\t\n\f ]/;
  var ALPHA = /[A-Za-z]/;
  var CRLF = /\r\n?/g;

  function isSpace(char) {
    return WSP.test(char);
  }

  function isAlpha(char) {
    return ALPHA.test(char);
  }

  function preprocessInput(input) {
    return input.replace(CRLF, "\n");
  }
});
define('simple-html-tokenizer', ['exports', 'module', './simple-html-tokenizer/html5-named-char-refs', './simple-html-tokenizer/entity-parser', './simple-html-tokenizer/evented-tokenizer', './simple-html-tokenizer/tokenizer', './simple-html-tokenizer/tokenize'], function (exports, module, _simpleHtmlTokenizerHtml5NamedCharRefs, _simpleHtmlTokenizerEntityParser, _simpleHtmlTokenizerEventedTokenizer, _simpleHtmlTokenizerTokenizer, _simpleHtmlTokenizerTokenize) {
	'use strict';

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

	var _HTML5NamedCharRefs = _interopRequireDefault(_simpleHtmlTokenizerHtml5NamedCharRefs);

	var _EntityParser = _interopRequireDefault(_simpleHtmlTokenizerEntityParser);

	var _EventedTokenizer = _interopRequireDefault(_simpleHtmlTokenizerEventedTokenizer);

	var _Tokenizer = _interopRequireDefault(_simpleHtmlTokenizerTokenizer);

	var _tokenize = _interopRequireDefault(_simpleHtmlTokenizerTokenize);

	var HTML5Tokenizer = {
		HTML5NamedCharRefs: _HTML5NamedCharRefs['default'],
		EntityParser: _EntityParser['default'],
		EventedTokenizer: _EventedTokenizer['default'],
		Tokenizer: _Tokenizer['default'],
		tokenize: _tokenize['default']
	};

	module.exports = HTML5Tokenizer;
});
define('linkify-html', ['exports', 'module', './simple-html-tokenizer', './linkify'], function (exports, module, _simpleHtmlTokenizer, _linkify) {
	'use strict';

	module.exports = linkifyHtml;

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

	var _HTML5Tokenizer = _interopRequireDefault(_simpleHtmlTokenizer);

	var StartTag = 'StartTag';
	var EndTag = 'EndTag';
	var Chars = 'Chars';
	var Comment = 'Comment';

	/**
 	`tokens` and `token` in this section refer to tokens generated by the HTML
 	parser.
 */

	function linkifyHtml(str) {
		var opts = arguments.length <= 1 || arguments[1] === undefined ? {} : arguments[1];

		var tokens = _HTML5Tokenizer['default'].tokenize(str);
		var linkifiedTokens = [];
		var linkified = [];
		var i;

		opts = _linkify.options.normalize(opts);

		// Linkify the tokens given by the parser
		for (i = 0; i < tokens.length; i++) {
			var token = tokens[i];

			if (token.type === StartTag) {
				linkifiedTokens.push(token);

				// Ignore all the contents of ignored tags
				var tagName = token.tagName.toUpperCase();
				var isIgnored = tagName === 'A' || opts.ignoreTags.indexOf(tagName) >= 0;
				if (!isIgnored) continue;

				var preskipLen = linkifiedTokens.length;
				skipTagTokens(tagName, tokens, ++i, linkifiedTokens);
				i += linkifiedTokens.length - preskipLen - 1;
				continue;
			} else if (token.type !== Chars) {
				// Skip this token, it's not important
				linkifiedTokens.push(token);
				continue;
			}

			// Valid text token, linkify it!
			var linkifedChars = linkifyChars(token.chars, opts);
			linkifiedTokens.push.apply(linkifiedTokens, linkifedChars);
		}

		// Convert the tokens back into a string
		for (i = 0; i < linkifiedTokens.length; i++) {
			var token = linkifiedTokens[i];
			switch (token.type) {
				case StartTag:
					var attrs = attrsToStrings(token.attributes);
					var link = '<' + token.tagName;
					if (attrs.length > 0) {
						link += ' ' + attrs.join(' ');
					}
					link += '>';
					linkified.push(link);
					break;
				case EndTag:
					linkified.push('</' + token.tagName + '>');
					break;
				case Chars:
					linkified.push(escapeText(token.chars));
					break;
				case Comment:
					linkified.push('<!--' + escapeText(token.chars) + '-->');
					break;
			}
		}

		return linkified.join('');
	}

	/**
 	`tokens` and `token` in this section referes to tokens returned by
 	`linkify.tokenize`. `linkified` will contain HTML Parser-style tokens
 */
	function linkifyChars(str, opts) {
		var tokens = _linkify.tokenize(str);
		var result = [];

		for (var i = 0; i < tokens.length; i++) {
			var token = tokens[i];
			var validated = token.isLink && _linkify.options.resolve(opts.validate, token.toString(), token.type);

			if (token.type === 'nl' && opts.nl2br) {
				result.push({
					type: StartTag,
					tagName: 'br',
					attributes: [],
					selfClosing: true
				});
				continue;
			} else if (!token.isLink || !validated) {
				result.push({ type: Chars, chars: token.toString() });
				continue;
			}

			var href = token.toHref(opts.defaultProtocol);
			var formatted = _linkify.options.resolve(opts.format, token.toString(), token.type);
			var formattedHref = _linkify.options.resolve(opts.formatHref, href, token.type);
			var attributesHash = _linkify.options.resolve(opts.attributes, href, token.type);
			var tagName = _linkify.options.resolve(opts.tagName, href, token.type);
			var linkClass = _linkify.options.resolve(opts.linkClass, href, token.type);
			var target = _linkify.options.resolve(opts.target, href, token.type);

			// Build up attributes
			var attributes = [['href', formattedHref], ['class', linkClass]];

			if (target) {
				attributes.push(['target', target]);
			}

			for (var attr in attributesHash) {
				attributes.push([attr, attributesHash[attr]]);
			}

			// Add the required tokens
			result.push({
				type: StartTag,
				tagName: tagName,
				attributes: attributes,
				selfClosing: false
			});
			result.push({ type: Chars, chars: formatted });
			result.push({ type: EndTag, tagName: tagName });
		}

		return result;
	}

	/**
 	Returns a list of tokens skipped until the closing tag of tagName.
 
 	* `tagName` is the closing tag which will prompt us to stop skipping
 	* `tokens` is the array of tokens generated by HTML5Tokenizer which
 	* `i` is the index immediately after the opening tag to skip
 	* `skippedTokens` is an array which skipped tokens are being pushed into
 
 	Caveats
 
 	* Assumes that i is the first token after the given opening tagName
 	* The closing tag will be skipped, but nothing after it
 	* Will track whether there is a nested tag of the same type
 */
	function skipTagTokens(tagName, tokens, i, skippedTokens) {

		// number of tokens of this type on the [fictional] stack
		var stackCount = 1;

		while (i < tokens.length && stackCount > 0) {
			var token = tokens[i];
			if (token.type === StartTag && token.tagName.toUpperCase() === tagName) {
				// Nested tag of the same type, "add to stack"
				stackCount++;
			} else if (token.type === EndTag && token.tagName.toUpperCase() === tagName) {
				// Closing tag
				stackCount--;
			}
			skippedTokens.push(token);
			i++;
		}

		// Note that if stackCount > 0 here, the HTML is probably invalid
		return skippedTokens;
	}

	function escapeText(text) {
		// Not required, HTML tokenizer ensures this occurs properly
		return text;
	}

	function escapeAttr(attr) {
		return attr.replace(/"/g, '&quot;');
	}

	function attrsToStrings(attrs) {
		var attrStrs = [];
		for (var i = 0; i < attrs.length; i++) {
			var _attrs$i = attrs[i];
			var _name = _attrs$i[0];
			var value = _attrs$i[1];

			attrStrs.push(_name + '="' + escapeAttr(value) + '"');
		}
		return attrStrs;
	}
});