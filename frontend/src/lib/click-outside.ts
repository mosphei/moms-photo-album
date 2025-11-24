// clickOutside.js
export function clickOutside(node: any, callback: () => void) {
	const handleClick = (event: any) => {
		if (node && !node.contains(event.target) && !event.defaultPrevented) {
			callback();
		}
	};

	document.addEventListener('click', handleClick, true); // Use `true` for capture phase

	return {
		destroy() {
			document.removeEventListener('click', handleClick, true);
		}
	};
}
