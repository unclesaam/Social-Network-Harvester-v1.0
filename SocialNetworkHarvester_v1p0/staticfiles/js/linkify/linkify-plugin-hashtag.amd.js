define('linkify/plugins/hashtag', ['exports', 'module'], function (exports, module) {
	/**
 	Quick Hashtag parser plugin for linkify
 */
	'use strict';

	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError('Cannot call a class as a function'); } }

	function _inherits(subClass, superClass) { if (typeof superClass !== 'function' && superClass !== null) { throw new TypeError('Super expression must either be null or a function, not ' + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

	function hashtag(linkify) {
		var TT = linkify.scanner.TOKENS,
		    // Text tokens
		MT = linkify.parser.TOKENS,
		    // Multi tokens
		MultiToken = MT.Base,
		    S_START = linkify.parser.start,
		    S_HASH = undefined,
		    S_HASHTAG = undefined;

		var HASHTAG = (function (_MultiToken) {
			_inherits(HASHTAG, _MultiToken);

			function HASHTAG(value) {
				_classCallCheck(this, HASHTAG);

				_MultiToken.call(this, value);
				this.type = 'hashtag';
				this.isLink = true;
			}

			return HASHTAG;
		})(MultiToken);

		S_HASH = new linkify.parser.State();
		S_HASHTAG = new linkify.parser.State(HASHTAG);

		S_START.on(TT.POUND, S_HASH);
		S_HASH.on(TT.DOMAIN, S_HASHTAG);
		S_HASH.on(TT.TLD, S_HASHTAG);
	}

	module.exports = hashtag;
});
require(['linkify', 'linkify/plugins/hashtag'], function (linkify, hashtag) {
	hashtag(linkify);
});