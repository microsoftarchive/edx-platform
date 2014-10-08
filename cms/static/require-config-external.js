require.config({
    paths: {
        // "gettext": "/i18n",
        // "xmodule": "/xmodule/xmodule",
        // "tender": [
        //     "//edxedge.tenderapp.com/tender_widget",
        //     // if tender fails to load, fallback on a local file
        //     // so that require doesn't fall over
        //     "js/src/tender_fallback"
        // ],
        // "mathjax": "//edx-static.s3.amazonaws.com/mathjax-MathJax-727332c/MathJax.js?config=TeX-MML-AM_HTMLorMML-full&delayStartupUntil=configured",
        // "youtube": [
        //     // youtube URL does not end in ".js". We add "?noext" to the path so
        //     // that require.js adds the ".js" to the query component of the URL,
        //     // and leaves the path component intact.
        //     "//www.youtube.com/player_api?noext",
        //     // if youtube fails to load, fallback on a local file
        //     // so that require doesn't fall over
        //     "js/src/youtube_fallback"
        // ]
    },
    shim: {
        // "gettext": {
        //     exports: "gettext"
        // },
        // "tender": {
        //     exports: 'Tender'
        // },
        // "youtube": {
        //     exports: "YT"
        // },
        // "mathjax": {
        //     exports: "MathJax",
        //     init: function() {
        //         MathJax.Hub.Config({
        //             tex2jax: {
        //                 inlineMath: [
        //                     ["\\(","\\)"],
        //                     ['[mathjaxinline]','[/mathjaxinline]']
        //                 ],
        //                 displayMath: [
        //                     ["\\[","\\]"],
        //                     ['[mathjax]','[/mathjax]']
        //                 ]
        //             }
        //         });
        //         MathJax.Hub.Configured();
        //     }
        // },
    }
});
