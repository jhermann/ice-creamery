(function() {
    const customDynamicStyle = document.createElement("style");
    // We must put it outside of the head and body, since they are replaced by the instant navigation feature in the Material theme
    document.documentElement.appendChild(customDynamicStyle);

    const TOGGLE_BUTTON_REFERENCE_ELEMENT_NOT_FOUND_WARNING = "[mkdocs-toggle-sidebar-plugin] Reference element for inserting 'toggle_button' not found. This version of the plugin may not be compatible with this version of the theme. Try updating both to the latest version. If that fails, you can open an GitHub issue.";

    const loadBool = (name, default_value) => {
        const value = localStorage.getItem(`TOGGLE_SIDEBAR_${name}`);
        if (value == null) {
            return default_value;
        } else {
            return value == "1";
        }
    }

    const loadNavigationState = () => loadBool("NAVIGATION", true);
    const loadTocState = () => loadBool("TOC", true);

    const saveBool = (name, value) => {
        localStorage.setItem(`TOGGLE_SIDEBAR_${name}`, value ? "1" : "0");
    }

    const toggleVisibility = (toggleNavigation, toggleTOC) => {
        let newNavigation = loadNavigationState();
        let newTOC = loadTocState();
        
        if (toggleNavigation) {
            newNavigation = !newNavigation;
            saveBool("NAVIGATION", newNavigation);
        }
        if (toggleTOC) {
            newTOC = !newTOC;
            saveBool("TOC", newTOC);
        }
        
        _setVisibility(newNavigation, newTOC);
    }

    const _setVisibility = (newNavigation, newTOC) => {
        console.debug(`Setting new visibility: navigation=${newNavigation}, TOC=${newTOC}`);
        // combine this into one operation, so that it is more efficient (for toggling both) and easier to code with dynamic CSS generation
        customDynamicStyle.innerHTML = setCombinedVisibility(newNavigation, newTOC);
    }

    // START OF INCLUDE
    // This gets replaced with the definitions of: 
    // - setCombinedVisibility(showNavigation: bool, showTOC: bool) -> string (dynamic CSS)
    // - registerKeyboardEventHandler() -> void
    const setCombinedVisibility = (showNavigation, showTOC) => {
    // Hide the button when on mobile (and menu us shown as hamburger menu anyways).
    // Uses the 60em threshold that is used for hiding the TOC, search bar, repo info (name + stars), etc

    let style = `
.mkdocs-toggle-sidebar-button {
    cursor: pointer;
    margin-right: 5px;
    margin-left: 1rem;
}

@media screen and (max-width: 60em) {
    .mkdocs-toggle-sidebar-button {
        display: none;
    }
}
`;
// The TOC has a different break point than the navigation.
// It can be seen on the nav.md-nav--secondary:nth-child(1) element (60em)
// If the screen is smaller, it is shown in the navigation section if you click the nested hamburger menu
if (!showTOC) {
    style += `
@media screen and (min-width: 60em) {
    div.md-sidebar.md-sidebar--secondary {
        display: none;
    }
}
`;
        }
        
    // We always have to show the navigation in mobile view, otherwise the hamburger menu is broken
    // In material for mkdocs's blog mode, navigation's class is '.md-sidebar--post', see #9
    // The exact width (76.1875em) is taken from the styling of the 'body > header > nav > a' element, I think
    if (!showNavigation) {
        style += `
@media screen and (min-width: 76.1875em) {
    div.md-sidebar.md-sidebar--primary, div.md-sidebar.md-sidebar--post {
        display: none;
    }
}
`;
    }

    return style;
}

const addToggleButton = (toggleNavigation, toggleTOC) => {
    const toggleBtn = createDefaultToggleButton(toggleNavigation, toggleTOC);
    toggleBtn.classList.add("md-icon");
  
    const titleElement = document.querySelector(".md-header__title");
    if (titleElement) {
        titleElement.parentNode.insertBefore(toggleBtn, titleElement.nextSibling);  
    } else {
        console.warn(TOGGLE_BUTTON_REFERENCE_ELEMENT_NOT_FOUND_WARNING);
    }
}

const registerKeyboardEventHandler = () => {
    // Custom key handlers: SEE https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/?h=key+bind#docsjavascriptsshortcutsjs
    keyboard$.subscribe(key => {
        if (key.mode === "global") {
            if (coreEventListenerLogic(key.type)) {
                // event handled, stop propagation
                key.claim();
            }
        }
    });
}

    // END OF INCLUDE

    // argument: string, returns true if the key was handled and the event should be marked as already handled
    const coreEventListenerLogic = (keyChar) => {
        if (keyChar === "t") {
            toggleVisibility(false, true);
            return true;
        } else if (keyChar === "m") {
            toggleVisibility(true, false);
            return true;
        } else if (keyChar === "b") {
            toggleVisibility(true, true);
            return true;
        } else {
            return false;
        }
    }

    const onPageLoadedAction = () => {
        console.log("The mkdocs-toggle-sidebar-plugin is installed. It adds the following key bindings:\n T -> toggle table of contents sidebar\n M -> toggle navigation menu sidebar\n B -> toggle both sidebars (TOC and navigation)");

        const toggle_button = "toc";
        if (toggle_button == "none") {
            // do nothing
        } else if (toggle_button == "navigation") {
            addToggleButton(true, false);
        } else if (toggle_button == "toc") {
            addToggleButton(false, true);
        } else if (toggle_button == "all") {
            addToggleButton(true, true);
        } else {
            console.error(`[mkdocs-toggle-sidebar-plugin] Unknown value for toggle_button: '${toggleButtonType}'`);
        }

        registerKeyboardEventHandler();
    }

    const createDefaultToggleButton = (toggleNavigation, toggleTOC) => {
        const toggleBtn = document.createElement("div");
        toggleBtn.className = "mkdocs-toggle-sidebar-button";
        toggleBtn.innerHTML = "<svg width=\"24px\" height=\"24px\" viewBox=\"0 -1 32 32\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:sketch=\"http://www.bohemiancoding.com/sketch/ns\">\n  <g id=\"Page-1\" stroke=\"none\" stroke-width=\"1\" fill=\"none\" fill-rule=\"evenodd\" sketch:type=\"MSPage\" style=\"--darkreader-inline-stroke: none;\" data-darkreader-inline-stroke=\"\">\n    <g id=\"Icon-Set\" sketch:type=\"MSLayerGroup\" transform=\"translate(-464.000000, -672.000000)\" fill=\"#000000\" style=\"--darkreader-inline-fill: var(--darkreader-text-000000, #ffffff);\" data-darkreader-inline-fill=\"\">\n      <path d=\"M469,688 L481.273,688 L477.282,691.299 C476.89,691.69 476.89,692.326 477.282,692.718 C477.676,693.11 478.313,693.11 478.706,692.718 L484.686,687.776 C484.896,687.566 484.985,687.289 484.971,687.016 C484.985,686.742 484.896,686.465 484.686,686.255 L478.706,681.313 C478.313,680.921 477.676,680.921 477.282,681.313 C476.89,681.705 476.89,682.341 477.282,682.732 L481.235,686 L469,686 C468.447,686 468,686.447 468,687 C468,687.553 468.447,688 469,688 L469,688 Z M494,698 C494,699.104 493.104,700 492,700 L490,700 L490,674 L492,674 C493.104,674 494,674.896 494,676 L494,698 L494,698 Z M488,700 L468,700 C466.896,700 466,699.104 466,698 L466,676 C466,674.896 466.896,674 468,674 L488,674 L488,700 L488,700 Z M492,672 L468,672 C465.791,672 464,673.791 464,676 L464,698 C464,700.209 465.791,702 468,702 L492,702 C494.209,702 496,700.209 496,698 L496,676 C496,673.791 494.209,672 492,672 L492,672 Z\" id=\"align-right\" sketch:type=\"MSShapeGroup\">\n      </path>\n    </g>\n  </g>\n</svg>";
        if (toggleNavigation && toggleTOC) {
            toggleBtn.title = "Toggle Navigation and Table of Contents";
        } else if (toggleNavigation) {
            toggleBtn.title = "Toggle Navigation";
        } else if (toggleTOC) {
            toggleBtn.title = "Toggle Table of Contents";
        }
        toggleBtn.addEventListener("click", () => toggleVisibility(toggleNavigation, toggleTOC));
        return toggleBtn;
    };

    // Export functions that the user can call to modify the state
    window.MkdocsToggleSidebarPlugin = {
        setNavigationVisibility: (show) => {
            saveBool("NAVIGATION", show);
            _setVisibility(show, loadTocState());
        },
        setTocVisibility: (show) => {
            saveBool("TOC", show);
            _setVisibility(loadNavigationState(), show);
        },
        setAllVisibility: (showNavigation, showTOC) => {
            saveBool("NAVIGATION", showNavigation);
            saveBool("TOC", showTOC);
            _setVisibility(showNavigation, showTOC);
        },
        toggleNavigationVisibility: () => toggleVisibility(true, false),
        toggleTocVisibility: () => toggleVisibility(false, true),
        toggleAllVisibility: () => toggleVisibility(true, true)
    };

    // Run this immediately instead of waiting for page.onload to prevent page flicker
    customDynamicStyle.innerHTML = setCombinedVisibility(loadNavigationState(), loadTocState());
    // console.log("Debug: hide sidebar completed");

    // SEE https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event#checking_whether_loading_is_already_complete
    if (document.readyState === "loading") {
        // console.debug("Registering DOMContentLoaded event listener");
        document.addEventListener("DOMContentLoaded", onPageLoadedAction);
    } else {
        // console.debug("DOMContentLoaded has already fired");
        onPageLoadedAction();
    }
}());
